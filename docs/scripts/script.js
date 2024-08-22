function openTab(evt, tabId) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tab-button");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabId).style.display = "block";
    evt.currentTarget.className += " active";
}

// Open the default tab
document.getElementsByClassName("tab-button")[0].click();

document.addEventListener("DOMContentLoaded", function () {
    const codeBlocks = document.querySelectorAll('pre');

    codeBlocks.forEach(pre => {
        // Cria o ícone de cópia
        const copyButton = document.createElement('button');
        copyButton.classList.add('copy-button');
        const originalIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M16 1h-10c-1.104 0-2 .896-2 2v14h-2v5h15v-2h3v-17h-4zm2 4h-10v-2h10v2zm0 12h-10v-12h10v12zm-11 6v-12h-3v12h3zm3-6v-2h6v2h-6zm0 4v-2h6v2h-6z"/></svg>';
        copyButton.innerHTML = originalIcon;

        // Adiciona o botão ao bloco de código
        pre.appendChild(copyButton);

        // Evento de clique para copiar o texto
        copyButton.addEventListener('click', function () {
            const code = pre.querySelector('code').innerText;
            navigator.clipboard.writeText(code).then(() => {
                copyButton.textContent = 'Copiado!';
                
                // Volta para o ícone original após 3 segundos
                setTimeout(() => {
                    copyButton.innerHTML = originalIcon;
                }, 3000);
            });
        });
    });
});
