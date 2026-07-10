(() => {
    let data = null;
    let deck = [];
    let currentIndex = 0;
    let mode = 'mc'; // 'mc' or 'answer'
    let score = { correct: 0, answered: 0 };
    let answered = false;
    let distractorsMap = {};
    let currentChoices = [];

    const els = {
        modeMc: document.getElementById('mode-mc'),
        modeAnswer: document.getElementById('mode-answer'),
        categoryToggle: document.getElementById('category-toggle'),
        resetBtn: document.getElementById('reset'),
        scoreText: document.getElementById('score'),
        cardImage: document.getElementById('card-image'),
        cardCategory: document.getElementById('card-category'),
        cardProgress: document.getElementById('card-progress'),
        choicesDiv: document.getElementById('choices'),
        revealBtn: document.getElementById('reveal'),
        answerText: document.getElementById('answer'),
        nextBtn: document.getElementById('next'),
        endSection: document.getElementById('end'),
        resultText: document.getElementById('result'),
        restartBtn: document.getElementById('restart'),
        errorText: document.getElementById('error'),
        gameSection: document.getElementById('game'),
        mcRegion: document.getElementById('mc-region'),
        answerRegion: document.getElementById('answer-region')
    };

    function shuffle(arr) {
        const result = arr.slice();
        for (let i = result.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [result[i], result[j]] = [result[j], result[i]];
        }
        return result;
    }

    async function init() {
        try {
            const resCards = await fetch('cards.json');
            if (!resCards.ok) throw new Error('Failed to load cards.json');
            data = await resCards.json();
            
            try {
                const resDist = await fetch('distractors.json');
                if (resDist.ok) {
                    distractorsMap = await resDist.json();
                }
            } catch (e) {
                // Ignore missing distractors
            }
            
            setupEvents();
            resetGame();
        } catch (e) {
            els.errorText.textContent = e.message;
            els.errorText.style.display = 'block';
            els.gameSection.style.display = 'none';
        }
    }

    function resetGame() {
        deck = shuffle(data.cards);
        currentIndex = 0;
        score = { correct: 0, answered: 0 };
        els.endSection.style.display = 'none';
        els.gameSection.style.display = 'block';
        updateModeUI();
        render();
    }

    function setMode(newMode) {
        if (mode === newMode) return;
        mode = newMode;
        deck = shuffle(data.cards);
        currentIndex = 0;
        score = { correct: 0, answered: 0 };
        els.endSection.style.display = 'none';
        els.gameSection.style.display = 'block';
        updateModeUI();
        render();
    }

    function updateModeUI() {
        els.modeMc.setAttribute('aria-pressed', mode === 'mc' ? 'true' : 'false');
        els.modeAnswer.setAttribute('aria-pressed', mode === 'answer' ? 'true' : 'false');
        
        if (mode === 'mc') {
            els.scoreText.style.display = 'block';
            els.mcRegion.style.display = 'block';
            els.answerRegion.style.display = 'none';
            els.scoreText.textContent = `Score: ${score.correct} / ${score.answered}`;
        } else {
            els.scoreText.style.display = 'none';
            els.mcRegion.style.display = 'none';
            els.answerRegion.style.display = 'block';
        }
    }

    function getDistractors(card) {
        let pool = [];
        const seen = new Set([card.definition]);

        function addCandidates(candidates) {
            for (const cand of candidates) {
                if (pool.length >= 3) break;
                if (!seen.has(cand)) {
                    pool.push(cand);
                    seen.add(cand);
                }
            }
        }

        // 1. From distractors.json
        const specificDistractors = distractorsMap[card.id] || [];
        addCandidates(shuffle(specificDistractors));

        // 2. Same category
        if (pool.length < 3) {
            const sameCategory = data.cards
                .filter(c => c.category === card.category && c.id !== card.id)
                .map(c => c.definition);
            addCandidates(shuffle(sameCategory));
        }

        // 3. Any category
        if (pool.length < 3) {
            const allDefinitions = data.cards
                .filter(c => c.id !== card.id)
                .map(c => c.definition);
            addCandidates(shuffle(allDefinitions));
        }

        return pool;
    }

    function applyCategoryVisibility() {
        if (els.categoryToggle.checked) {
            els.cardCategory.classList.remove('hidden');
        } else {
            els.cardCategory.classList.add('hidden');
        }
    }

    function render() {
        answered = false;
        els.nextBtn.disabled = true;
        els.choicesDiv.innerHTML = '';
        currentChoices = [];

        const card = deck[currentIndex];
        els.cardImage.src = card.image;
        els.cardCategory.textContent = card.category;
        applyCategoryVisibility();
        els.cardProgress.textContent = `Card ${currentIndex + 1} / ${deck.length}`;

        if (mode === 'mc') {
            els.scoreText.textContent = `Score: ${score.correct} / ${score.answered}`;
            const distractors = getDistractors(card);
            currentChoices = shuffle([card.definition, ...distractors]);

            currentChoices.forEach((choiceText, i) => {
                const btn = document.createElement('button');
                btn.textContent = choiceText;
                btn.className = 'choice-btn';
                btn.onclick = () => handleMcAnswer(i);
                els.choicesDiv.appendChild(btn);
            });
        } else {
            els.answerText.textContent = '';
            els.answerText.hidden = true;
            els.revealBtn.style.display = 'inline-block';
            els.revealBtn.focus();
        }
    }

    function handleMcAnswer(selectedIndex) {
        if (answered) return;
        answered = true;
        const card = deck[currentIndex];
        const buttons = els.choicesDiv.querySelectorAll('button');
        
        let isCorrect = currentChoices[selectedIndex] === card.definition;
        
        score.answered++;
        if (isCorrect) {
            score.correct++;
        }

        buttons.forEach((btn, i) => {
            btn.disabled = true;
            if (currentChoices[i] === card.definition) {
                btn.classList.add('correct');
            } else if (i === selectedIndex && !isCorrect) {
                btn.classList.add('incorrect');
            }
        });

        els.scoreText.textContent = `Score: ${score.correct} / ${score.answered}`;
        els.nextBtn.disabled = false;
        els.nextBtn.focus();
    }

    function handleReveal() {
        if (answered) return;
        answered = true;
        els.revealBtn.style.display = 'none';
        els.answerText.textContent = deck[currentIndex].definition;
        els.answerText.hidden = false;
        els.nextBtn.disabled = false;
        els.nextBtn.focus();
    }

    function nextCard() {
        currentIndex++;
        if (currentIndex >= deck.length) {
            els.gameSection.style.display = 'none';
            els.endSection.style.display = 'block';
            if (mode === 'mc') {
                els.resultText.textContent = `You scored ${score.correct} out of ${deck.length}`;
            } else {
                els.resultText.textContent = `Deck complete \u2014 ${deck.length} cards reviewed`;
            }
            els.restartBtn.focus();
        } else {
            render();
        }
    }

    function setupEvents() {
        els.modeMc.addEventListener('click', () => setMode('mc'));
        els.modeAnswer.addEventListener('click', () => setMode('answer'));
        els.categoryToggle.addEventListener('change', applyCategoryVisibility);
        els.resetBtn.addEventListener('click', resetGame);
        els.restartBtn.addEventListener('click', resetGame);
        els.nextBtn.addEventListener('click', nextCard);
        els.revealBtn.addEventListener('click', handleReveal);

        document.addEventListener('keydown', (e) => {
            if (e.key >= '1' && e.key <= '4' && mode === 'mc' && !answered) {
                const idx = parseInt(e.key) - 1;
                if (idx < currentChoices.length) {
                    handleMcAnswer(idx);
                }
            } else if ((e.key === 'Enter' || e.key === ' ') && els.gameSection.style.display !== 'none') {
                const isExcludedEl = document.activeElement === els.resetBtn ||
                                     document.activeElement === els.modeMc ||
                                     document.activeElement === els.modeAnswer ||
                                     document.activeElement === els.categoryToggle;
                if (mode === 'mc' && answered) {
                    if (!isExcludedEl) {
                        e.preventDefault();
                        nextCard();
                    }
                } else if (mode === 'answer') {
                    if (!isExcludedEl) {
                        e.preventDefault();
                        if (!answered) {
                            handleReveal();
                        } else {
                            nextCard();
                        }
                    }
                }
            }
        });
    }

    init();
})();
