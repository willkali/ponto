// horario_trabalho.js

function calcularHoras() {
    let totalHoras = 0;

    for (let i = 1; i <= 7; i++) {
        const trabalhar = document.getElementById(`trabalhar_${i}`).checked;
        const entrada = document.getElementById(`entrada_${i}`).value;
        const saida = document.getElementById(`saida_${i}`).value;
        const intervalo = document.getElementById(`intervalo_${i}`).value;

        if (trabalhar && entrada && saida) {
            const entradaDate = new Date(`1970-01-01T${entrada}:00`);
            const saidaDate = new Date(`1970-01-01T${saida}:00`);
            let horasTrabalhadas = (saidaDate - entradaDate) / (1000 * 60 * 60); // Converte para horas

            if (intervalo) {
                horasTrabalhadas -= intervalo / 60; // Subtrai o intervalo em horas
            }

            document.getElementById(`carga_horaria_${i}`).innerText = horasTrabalhadas.toFixed(2);
            totalHoras += horasTrabalhadas;
        } else {
            document.getElementById(`carga_horaria_${i}`).innerText = '0';
        }
    }

    document.getElementById('totalHoras').innerText = totalHoras.toFixed(2);
}

// Adiciona ouvintes de eventos aos campos para recalcular automaticamente
function adicionarOuvintesDeEvento() {
    for (let i = 1; i <= 7; i++) {
        const checkbox = document.getElementById(`trabalhar_${i}`);
        const entrada = document.getElementById(`entrada_${i}`);
        const saida = document.getElementById(`saida_${i}`);
        const intervalo = document.getElementById(`intervalo_${i}`);

        checkbox.addEventListener('change', calcularHoras);
        entrada.addEventListener('change', calcularHoras);
        saida.addEventListener('change', calcularHoras);
        intervalo.addEventListener('input', calcularHoras);
    }
}

// Executa a função adicionarOuvintesDeEvento quando o DOM estiver completamente carregado
document.addEventListener('DOMContentLoaded', adicionarOuvintesDeEvento);
