<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $email = $_POST['email'];
    $senha = $_POST['senha'];

    // Exemplo de verificação de usuário e senha
    $usuario_valido = 'usuario@exemplo.com';
    $senha_valida = 'senha123';

    if ($email == $usuario_valido && $senha == $senha_valida) {
        $_SESSION['usuario'] = $email;
        header('Location: dashboard.php'); // Redireciona para a página do dashboard
        exit();
    } else {
        $erro = 'E-mail ou senha incorretos.';
    }
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login de Usuário</title>

    <!-- REFERENCIA CSS -->
    <link rel="stylesheet" href="/static/bootstrap.min.css" />
    <link rel="stylesheet" href="/static/login.css" />
    <link rel="stylesheet" href="/static/font-awesome.css" />
</head>
<body>
    <div class="container mt-5">
        <div class="card">
            <div class="card-header text-center">
                <h2>Login de Usuário</h2>
            </div>
            <div class="card-body">
                <?php if (isset($erro)): ?>
                    <div class="alert alert-danger" role="alert">
                        <?php echo htmlspecialchars($erro); ?>
                    </div>
                <?php endif; ?>
                <form action="login.php" method="post">
                    <!-- Informações de Login -->
                    <fieldset>
                        <legend>Informações de Login</legend>
                        <div class="form-row">
                            <div class="form-group col-md-12">
                                <label for="email">E-mail:</label>
                                <div class="input-group">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                    </div>
                                    <input type="email" id="email" name="email" class="form-control" required placeholder="seuemail@dominio.com">
                                </div>
                            </div>
                            <div class="form-group col-md-12">
                                <label for="senha">Senha:</label>
                                <div class="input-group">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                    </div>
                                    <input type="password" id="senha" name="senha" class="form-control" required placeholder="Digite sua senha">
                                </div>
                            </div>
                        </div>
                    </fieldset>
                    <button type="submit" class="btn btn-primary btn-block">Entrar</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
