let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    
    // Show the install button
    const installButton = document.querySelector('#installApp');
    if (installButton) {
        installButton.style.display = 'block';
        
        installButton.addEventListener('click', async () => {
            if (deferredPrompt) {
                // Show the prompt
                deferredPrompt.prompt();
                // Wait for the user to respond to the prompt
                const { outcome } = await deferredPrompt.userChoice;
                // We no longer need the prompt. Clear it up
                deferredPrompt = null;
            }
        });
    }
}); 