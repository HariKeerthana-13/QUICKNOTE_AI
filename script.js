document.addEventListener('DOMContentLoaded', () => {
    // --- Get all the new elements ---
    const ttsSettings = document.getElementById('tts-settings');
    const voiceSearch = document.getElementById('voice-search');
    const voiceSelect = document.getElementById('voice-select');
    const rateSlider = document.getElementById('rate-slider');
    const rateValue = document.getElementById('rate-value');
    
    const processButton = document.getElementById('processButton');
    const listenButton = document.getElementById('listenButton');
    const inputText = document.getElementById('inputText');
    const summaryOutput = document.getElementById('summaryOutput');
    const actionItemsOutput = document.getElementById('actionItemsOutput');
    const loader = document.getElementById('loader');
    
    let currentAudio = null;
    let allVoices = []; // NEW: This will be our master list of voices

    // --- MODIFIED: Function to populate voices ---
    async function loadVoices() {
        try {
            const response = await fetch('/api/tts-voices');
            allVoices = await response.json(); // Store in our master list
            populateVoiceList(); // Populate the list for the first time
        } catch (error) {
            console.error('Failed to load voices:', error);
        }
    }
    
    // --- MODIFIED: This function now filters AND re-builds the list ---
    function populateVoiceList() {
        const searchTerm = voiceSearch.value.toLowerCase();
        voiceSelect.innerHTML = ''; // Clear all current options

        // Loop through our master list (allVoices)
        for (let voice of allVoices) {
            const voiceName = `${voice.name} (${voice.lang[0]})`.toLowerCase();
            
            // If it matches, create a new option and add it
            if (voiceName.includes(searchTerm)) {
                const option = document.createElement('option');
                option.value = voice.id;
                option.textContent = `${voice.name} (${voice.lang[0]})`;
                voiceSelect.appendChild(option);
            }
        }
    }

    // --- Event listener for the rate slider ---
    rateSlider.addEventListener('input', () => {
        const rate = rateSlider.value;
        if (rate < 140) rateValue.textContent = 'Slow';
        else if (rate > 210) rateValue.textContent = 'Fast';
        else rateValue.textContent = 'Normal';
    });
    
    // --- MODIFIED: This listener now calls the new function ---
    voiceSearch.addEventListener('input', populateVoiceList);

    // --- Load voices on page start ---
    loadVoices();

    // --- processButton click listener (no changes) ---
    processButton.addEventListener('click', async () => {
        listenButton.disabled = true;
        ttsSettings.classList.add('hidden');
        if (currentAudio) currentAudio.pause();
        
        loader.classList.remove('hidden');
        summaryOutput.textContent = '';
        actionItemsOutput.innerHTML = '';
        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: inputText.value }),
            });
            if (!response.ok) throw new Error(`Server error: ${response.statusText}`);
            const data = await response.json();
            
            summaryOutput.textContent = data.summary;
            if (data.action_items && data.action_items.length > 0) {
                data.action_items.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    actionItemsOutput.appendChild(li);
                });
            } else {
                actionItemsOutput.innerHTML = '<li>No action items found.</li>';
            }

            if (data.summary) {
                listenButton.disabled = false;
                ttsSettings.classList.remove('hidden');
            }

        } catch (error) {
            console.error('Error:', error);
            summaryOutput.textContent = 'Failed to process text. See console for details.';
        } finally {
            loader.classList.add('hidden');
        }
    });

    // --- listenButton click listener (no changes) ---
    listenButton.addEventListener('click', async () => {
        const text = summaryOutput.textContent;
        if (!text || listenButton.disabled) return;

        if (currentAudio && !currentAudio.paused) {
            currentAudio.pause();
            listenButton.querySelector('span').textContent = 'Listen';
            return;
        }

        listenButton.disabled = true;
        listenButton.querySelector('span').textContent = 'Loading...';

        try {
            const voiceId = voiceSelect.value;
            const rate = rateSlider.value;
            
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, voice_id: voiceId, rate: rate }),
            });
            if (!response.ok) throw new Error('Failed to generate audio');

            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            currentAudio = new Audio(audioUrl);
            currentAudio.play();
            listenButton.querySelector('span').textContent = 'Pause';
            
            currentAudio.onended = () => {
                listenButton.querySelector('span').textContent = 'Listen';
            };
        } catch (error) {
            console.error('TTS Error:', error);
            alert('Could not generate audio.');
            listenButton.querySelector('span').textContent = 'Listen';
        } finally {
            listenButton.disabled = false;
        }
    });
});