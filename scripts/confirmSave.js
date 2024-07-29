document.getElementById('editForm').addEventListener('submit', function (e) {
    const confirmSave = confirm('Tem certeza que deseja alterar as informações?');
    if (!confirmSave) {
        e.preventDefault();  // Cancela o envio do formulário se o usuário clicar em "Cancelar"
    }
});
