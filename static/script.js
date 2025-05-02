document.addEventListener('DOMContentLoaded', function() {
  const generateBtn = document.getElementById('generate-btn');
  const userInput = document.getElementById('user-input');
  const styleSelect = document.getElementById('style-select');
  const tokenSlider = document.getElementById('token-slider');
  const tokenValue = document.getElementById('token-value');
  const resultText = document.getElementById('result-text');
  const copyBtn = document.getElementById('copy-btn');
  const resultBox = document.getElementById('result');
  
  // Update token value display
  tokenSlider.addEventListener('input', function() {
      tokenValue.textContent = this.value;
  });
  
  // Generate text on button click
  generateBtn.addEventListener('click', generateText);
  
  // Also generate on Enter key
  userInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
          generateText();
      }
  });
  
  // Copy to clipboard
  copyBtn.addEventListener('click', function() {
      const textToCopy = resultText.textContent;
      navigator.clipboard.writeText(textToCopy).then(() => {
          // Show feedback
          const originalText = copyBtn.innerHTML;
          copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
          copyBtn.style.backgroundColor = 'var(--success-color)';
          copyBtn.style.borderColor = 'var(--success-color)';
          copyBtn.style.color = 'white';
          
          setTimeout(() => {
              copyBtn.innerHTML = originalText;
              copyBtn.style.backgroundColor = '';
              copyBtn.style.borderColor = '';
              copyBtn.style.color = '';
          }, 2000);
      });
  });
  
  function generateText() {
      const text = userInput.value.trim();
      if (!text) {
          resultText.textContent = 'Please enter some text to start with.';
          return;
      }
      
      // Show loading state
      resultText.textContent = 'Generating...';
      resultBox.style.animation = 'pulse 1.5s infinite';
      
      fetch('/generate', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              text: text,
              style: styleSelect.value,
              max_tokens: tokenSlider.value
          })
      })
      .then(response => response.json())
      .then(data => {
          // Remove loading animation
          resultBox.style.animation = 'none';
          
          if (data.result) {
              resultText.textContent = data.result;
          } else {
              resultText.textContent = 'No prediction could be generated. Please try again.';
          }
      })
      .catch(error => {
          console.error('Error:', error);
          resultText.textContent = 'An error occurred. Please try again.';
          resultBox.style.animation = 'none';
      });
  }
});