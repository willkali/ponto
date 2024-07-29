<?php

// register.php

$host = '192.168.1.13';
$dbname = 'cadastro';
$user = 'postgres';
$password = 'reboot3';

// Conecta ao banco de dados
try {
    $pdo = new PDO("pgsql:host=$host;dbname=$dbname", $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Erro ao conectar ao banco de dados: " . $e->getMessage());
}

// Obtém os dados do formulário
$cpf = $_POST['cpf'];
$email = $_POST['email'];
$senha = password_hash($_POST['senha'], PASSWORD_DEFAULT);
$nome = $_POST['nome'];
$sobrenome = $_POST['sobrenome'];
$nascimento = DateTime::createFromFormat('d/m/Y', $_POST['nascimento'])->format('Y-m-d');
$rg = $_POST['rg'];
$sexo = $_POST['sexo'];
$cep = $_POST['cep'];
$endereco = $_POST['endereco'];
$numero = $_POST['numero'];
$bairro = $_POST['bairro'];
$complemento = $_POST['complemento'];
$cidade = $_POST['cidade'];
$estado = $_POST['estado'];
$telefone = $_POST['telefone'];
$celular = $_POST['celular'];

// Prepara a instrução SQL
$sql = "INSERT INTO usuarios (cpf, email, senha, nome, sobrenome, nascimento, rg, sexo, cep, endereco, numero, bairro, complemento, cidade, estado, telefone, celular) 
        VALUES (:cpf, :email, :senha, :nome, :sobrenome, :nascimento, :rg, :sexo, :cep, :endereco, :numero, :bairro, :complemento, :cidade, :estado, :telefone, :celular)";

$stmt = $pdo->prepare($sql);

// Executa a instrução SQL
try {
    $stmt->execute([
        ':cpf' => $cpf,
        ':email' => $email,
        ':senha' => $senha,
        ':nome' => $nome,
        ':sobrenome' => $sobrenome,
        ':nascimento' => $nascimento,
        ':rg' => $rg,
        ':sexo' => $sexo,
        ':cep' => $cep,
        ':endereco' => $endereco,
        ':numero' => $numero,
        ':bairro' => $bairro,
        ':complemento' => $complemento,
        ':cidade' => $cidade,
        ':estado' => $estado,
        ':telefone' => $telefone,
        ':celular' => $celular
    ]);
    echo "Cadastro realizado com sucesso!";
} catch (PDOException $e) {
    echo "Erro ao realizar cadastro: " . $e->getMessage();
}
?>
