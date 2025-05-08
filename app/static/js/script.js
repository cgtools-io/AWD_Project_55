document.addEventListener('DOMContentLoaded', () => {
    const coins = [
      { left: '5%', delay: '0s', duration: '5s' },
      { left: '20%', delay: '0.8s', duration: '6s' },
      { left: '40%', delay: '1.5s', duration: '7s' },
      { left: '60%', delay: '0.3s', duration: '5.5s' },
      { left: '80%', delay: '2s', duration: '6.5s' }
    ];
  
    const container = document.getElementById('coin-bg');
    if (container) {
      coins.forEach(c => {
        const div = document.createElement('div');
        div.className = 'coin';
        div.style.left = c.left;
        div.style.animationDelay = c.delay;
        div.style.animationDuration = c.duration;
        container.appendChild(div);
      });
    }
  });