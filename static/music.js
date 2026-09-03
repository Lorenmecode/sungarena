(function () {
  const button = document.querySelector("[data-music-toggle]");
  if (!button) return;

  let audioContext;
  let masterGain;
  let timer;
  let step = 0;
  let isPlaying = false;
  const progression = [
    [261.63, 329.63, 392.0],
    [220.0, 261.63, 329.63],
    [174.61, 220.0, 261.63],
    [196.0, 246.94, 293.66],
  ];

  function playChord() {
    const now = audioContext.currentTime;
    const chord = progression[step % progression.length];
    chord.forEach((frequency, index) => {
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      oscillator.type = index === 0 ? "sine" : "triangle";
      oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(index === 0 ? 0.045 : 0.022, now + 1.2);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 5.8);
      oscillator.connect(gain).connect(masterGain);
      oscillator.start(now);
      oscillator.stop(now + 6);
    });
    step += 1;
  }

  function startMusic() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    masterGain = audioContext.createGain();
    masterGain.gain.value = 0.7;
    masterGain.connect(audioContext.destination);
    playChord();
    timer = window.setInterval(playChord, 5200);
    isPlaying = true;
    button.textContent = "♫ Tắt nhạc";
    button.setAttribute("aria-pressed", "true");
    button.classList.add("is-playing");
  }

  function stopMusic() {
    window.clearInterval(timer);
    timer = null;
    isPlaying = false;
    button.textContent = "♫ Bật nhạc du dương";
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
