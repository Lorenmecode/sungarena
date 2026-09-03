(function () {
  const button = document.querySelector("[data-music-toggle]");
  if (!button) return;

  let audioContext;
  let masterGain;
  let timer;
  let noteIndex = 0;
  let isPlaying = false;
  const beat = 360;
  const melody = [
    ["G4", 1], ["G4", 1], ["A4", 2], ["G4", 2], ["C5", 2], ["B4", 4],
    ["G4", 1], ["G4", 1], ["A4", 2], ["G4", 2], ["D5", 2], ["C5", 4],
    ["G4", 1], ["G4", 1], ["G5", 2], ["E5", 2], ["C5", 2], ["B4", 2], ["A4", 4],
    ["F5", 1], ["F5", 1], ["E5", 2], ["C5", 2], ["D5", 2], ["C5", 4],
  ];
  const frequencies = {
    A4: 440, A5: 880, B4: 493.88, C5: 523.25, D5: 587.33,
    E5: 659.25, F5: 698.46, G4: 392, G5: 783.99,
  };

  function playNote() {
    const now = audioContext.currentTime;
    const [note, beats] = melody[noteIndex];
    const duration = beats * beat;
    const oscillator = audioContext.createOscillator();
    const gain = audioContext.createGain();
    oscillator.type = "sine";
    oscillator.frequency.value = frequencies[note];
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.11, now + 0.03);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration / 1000);
    oscillator.connect(gain).connect(masterGain);
    oscillator.start(now);
    oscillator.stop(now + duration / 1000);

    noteIndex = (noteIndex + 1) % melody.length;
    timer = window.setTimeout(playNote, duration);
  }

  function startMusic() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    masterGain = audioContext.createGain();
    masterGain.gain.value = 0.7;
    masterGain.connect(audioContext.destination);
    noteIndex = 0;
    playNote();
    isPlaying = true;
    button.textContent = "♫ Tắt nhạc";
    button.setAttribute("aria-pressed", "true");
    button.classList.add("is-playing");
  }

  function stopMusic() {
    window.clearTimeout(timer);
    timer = null;
    noteIndex = 0;
    isPlaying = false;
    button.textContent = "♫ Bật nhạc sinh nhật";
    button.setAttribute("aria-pressed", "false");
    button.classList.remove("is-playing");
    audioContext.close();
    audioContext = null;
  }

  button.addEventListener("click", function () {
    if (isPlaying) {
      stopMusic();
    } else {
      startMusic();
    }
  });
})();
