fetch('https://api.nasa.gov/planetary/apod?api_key=li9s96NxIGuSTKT6AM1vcBf75XEyzhnDecN1IGae')
  .then(response => response.json())
  .then(data => {
    // Extract the image URL from the response data
    const imageUrl = data.url;
    
    // Set the background image of the website
    document.body.style.backgroundImage = `url(${imageUrl})`;
  })
  .catch(error => {
    console.error('Error:', error);
  });
// Add this script in your JavaScript file (e.g., nasa-background.js)
window.addEventListener('DOMContentLoaded', () => {
  const backgroundElement = document.querySelector('.background-element');
  const maskOverlay = document.querySelector('.mask-overlay');

  // Calculate average brightness of the background image
  const calculateBrightness = () => {
    const image = new Image();
    image.src = getComputedStyle(backgroundElement).backgroundImage.slice(4, -1).replace(/"/g, '');

    image.onload = () => {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = image.width;
      canvas.height = image.height;

      context.drawImage(image, 0, 0);
      const imageData = context.getImageData(0, 0, image.width, image.height).data;

      let sum = 0;
      for (let i = 0; i < imageData.length; i += 4) {
        sum += (imageData[i] + imageData[i + 1] + imageData[i + 2]) / 3;
      }

      const averageBrightness = sum / (imageData.length / 4);
      const overlayOpacity = 1 - (averageBrightness / 255); // Adjust the opacity calculation as needed

      maskOverlay.style.backgroundColor = `rgba(0, 0, 0, ${overlayOpacity})`;
    };
  };

  calculateBrightness();

  // Recalculate brightness when the window is resized
  window.addEventListener('resize', calculateBrightness);
});
