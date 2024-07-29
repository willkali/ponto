function atualizaRelogio() {
    var agora = new Date();
    var data = agora.toLocaleDateString();
    var hora = agora.toLocaleTimeString();

    document.getElementById('data').innerHTML = data;
    document.getElementById('hora').innerHTML = hora;
}

// Chama a função quando a página é carregada
document.addEventListener('DOMContentLoaded', function () {
    atualizaRelogio();
    setInterval(atualizaRelogio, 1000);
});