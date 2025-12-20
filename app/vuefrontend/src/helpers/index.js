function isMobile() {
  const isAndroid = /android/i.test(navigator.userAgent);
  const isiOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const isWindowsPhone = /windows phone/i.test(navigator.userAgent);
  const isMobileSafari = /safari/i.test(navigator.userAgent) && /apple mobile/i.test(navigator.userAgent);

  return isAndroid || isiOS || isWindowsPhone || isMobileSafari || screen.width < 768;
}

function base64ToBlob(base64Data, contentType) {
  var sliceSize = 512;
  var byteCharacters = atob(base64Data);
  var byteArrays = [];

  for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    var slice = byteCharacters.slice(offset, offset + sliceSize);

    var byteNumbers = new Array(slice.length);
    for (var i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    var byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  return new Blob(byteArrays, { type: contentType });
}

export const openPdf = (data) => {
  const reportName = data.filename;

  setTimeout(() => {
    if (isMobile()) {
      const blob = base64ToBlob(data.file, data.file_type);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');

      link.href = url;
      link.download = data.filename;
      link.click();
      URL.revokeObjectURL(url);

    } else {
      const newWindow = window.open('', reportName);

      if (!newWindow) {
        alert("Popup blocked! Please allow popups for this site.");
        return;
      }

      const interval = setInterval(() => {
        if (newWindow.document && newWindow.document.body) {
          clearInterval(interval);

          const title = newWindow.document.createElement('title');
          const iframe = newWindow.document.createElement('iframe');

          title.appendChild(document.createTextNode(reportName));
          newWindow.document.head.appendChild(title);
          newWindow.document.body.setAttribute('style', 'margin: 0;');

          iframe.setAttribute('src', `data:application/pdf;base64,${data.file}`);
          iframe.setAttribute('width', "100%");
          iframe.setAttribute('height', "100%");
          iframe.setAttribute('style', "border:none;");

          newWindow.document.body.appendChild(iframe);
        }
      }, 100);

      // Seguridad: si en 5 segundos no carga, avisamos
      setTimeout(() => {
        if (!newWindow.document || !newWindow.document.body) {
          clearInterval(interval);
          alert("The document could not be loaded in time. Please try again.");
        }
      }, 7000);
    }
  }, 100);
};