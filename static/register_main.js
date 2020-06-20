/* Copyright 2013 Chris Wilson

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext();
var audioInput = null,
    realAudioInput = null,
    inputPoint = null,
    audioRecorder = null;
var rafID = null;
var analyserContext = null;
var canvasWidth, canvasHeight;
var recIndex = 0;


function gotBuffers(buffers) {
    audioRecorder.exportMonoWAV(doneEncoding);
}

function doneEncoding(soundBlob) {
    // fetch('/audio', {method: "POST", body: soundBlob}).then(response => $('#output').text(response.text()))
    // fetch('/audio', {method: "POST", body: soundBlob}).then(response => response.text().then(text => {
    //     document.getElementById('output').value = text;
    // }));


    fetch('/register_record_voice_audio', {method: "POST", body: soundBlob})
        .then(response => {
            response.text().then(text => document.getElementById('output').value = text);
            let message = document.createElement('div');
            let paragraph = document.querySelector("html>body.text-center>div.form-signin>div.container>p");
            paragraph.insertBefore(message, paragraph.firstChild);
            message.style.fontSize = "1.5em";
                if (response.status == 200){
                    console.log(response);
                    paragraph.style.color = "green";
                    message.innerText = 'No gratki, nagrałeś głos, za niecałe 3 sekund zostaniesz przekierowany do systemu...';
                    let counter = document.createElement('div');
                    paragraph.insertBefore(counter, message.nextElementSibling);
                    counter.style.fontSize = "2em";
                    let time = 3;
                        let countdown = setInterval(function () {
                            counter.innerText = time;
                            --time;
                            if (time < 0){
                                clearInterval(countdown);
                                document.location = document.location.protocol+ "//" + document.location.hostname + "/check_session";
                            }
                        }
                        ,1000);

                    // async function sleep(ms) {
                    //     await new Promise(r => setTimeout(r => {
                    //
                    //     }, ms));
                    // }
                    // sleep(5000);
                }else{
                    throw response.status;
                }
        })
        .catch(function(err){
            console.log(err);
            paragraph.style.color = "red";
            message.innerText = 'Ooops! Coś poszło nie tak (error ' + err + ')';

        });

    recIndex++;
}

function stopRecording() {
    // stop recording
    audioRecorder.stop();
    document.getElementById('stop').disabled = true;
    document.getElementById('start').removeAttribute('disabled');
    audioRecorder.getBuffers(gotBuffers);
    // location.reload()
}

function startRecording() {

    // start recording
    if (!audioRecorder)
        return;
    document.getElementById('start').disabled = true;
    document.getElementById('stop').removeAttribute('disabled');
    audioRecorder.clear();
    audioRecorder.record();
}

function convertToMono(input) {
    var splitter = audioContext.createChannelSplitter(2);
    var merger = audioContext.createChannelMerger(2);

    input.connect(splitter);
    splitter.connect(merger, 0, 0);
    splitter.connect(merger, 0, 1);
    return merger;
}

function cancelAnalyserUpdates() {
    window.cancelAnimationFrame(rafID);
    rafID = null;
}

function updateAnalysers(time) {
    if (!analyserContext) {
        var canvas = document.getElementById("analyser");
        canvasWidth = canvas.width;
        canvasHeight = canvas.height;
        analyserContext = canvas.getContext('2d');
    }

    // analyzer draw code here
    {
        var SPACING = 3;
        var BAR_WIDTH = 1;
        var numBars = Math.round(canvasWidth / SPACING);
        var freqByteData = new Uint8Array(analyserNode.frequencyBinCount);

        analyserNode.getByteFrequencyData(freqByteData);

        analyserContext.clearRect(0, 0, canvasWidth, canvasHeight);
        analyserContext.fillStyle = '#F6D565';
        analyserContext.lineCap = 'round';
        var multiplier = analyserNode.frequencyBinCount / numBars;

        // Draw rectangle for each frequency bin.
        for (var i = 0; i < numBars; ++i) {
            var magnitude = 0;
            var offset = Math.floor(i * multiplier);
            // gotta sum/average the block, or we miss narrow-bandwidth spikes
            for (var j = 0; j < multiplier; j++)
                magnitude += freqByteData[offset + j];
            magnitude = magnitude / multiplier;
            var magnitude2 = freqByteData[i * multiplier];
            analyserContext.fillStyle = "hsl( " + Math.round((i * 360) / numBars) + ", 100%, 50%)";
            analyserContext.fillRect(i * SPACING, canvasHeight, BAR_WIDTH, -magnitude);
        }
    }

    rafID = window.requestAnimationFrame(updateAnalysers);
}

function toggleMono() {
    if (audioInput != realAudioInput) {
        audioInput.disconnect();
        realAudioInput.disconnect();
        audioInput = realAudioInput;
    } else {
        realAudioInput.disconnect();
        audioInput = convertToMono(realAudioInput);
    }

    audioInput.connect(inputPoint);
}

function gotStream(stream) {
    document.getElementById('start').removeAttribute('disabled');

    inputPoint = audioContext.createGain();

    // Create an AudioNode from the stream.
    realAudioInput = audioContext.createMediaStreamSource(stream);
    audioInput = realAudioInput;
    audioInput.connect(inputPoint);

//    audioInput = convertToMono( input );

    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 2048;
    inputPoint.connect(analyserNode);

    audioRecorder = new Recorder(inputPoint);

    zeroGain = audioContext.createGain();
    zeroGain.gain.value = 0.0;
    inputPoint.connect(zeroGain);
    zeroGain.connect(audioContext.destination);
    updateAnalysers();
}

function initAudio() {
    if (!navigator.getUserMedia)
        navigator.getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
    if (!navigator.cancelAnimationFrame)
        navigator.cancelAnimationFrame = navigator.webkitCancelAnimationFrame || navigator.mozCancelAnimationFrame;
    if (!navigator.requestAnimationFrame)
        navigator.requestAnimationFrame = navigator.webkitRequestAnimationFrame || navigator.mozRequestAnimationFrame;

    navigator.getUserMedia(
        {
            "audio": {
                "mandatory": {
                    "googEchoCancellation": "false",
                    "googAutoGainControl": "false",
                    "googNoiseSuppression": "false",
                    "googHighpassFilter": "false"
                },
                "optional": []
            },
        }, gotStream, function (e) {
            alert('Error getting audio');
            console.log(e);
        });
}

window.addEventListener('load', initAudio);

function unpause() {
    document.getElementById('init').style.display = 'none';
    audioContext.resume().then(() => {
        console.log('Playback resumed successfully');
    });
}