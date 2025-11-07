-- =====================================================
-- MIGRAÇÕES DO SISTEMA DE CONTROLE DE GASTOS
-- Schema: cli_gastos
-- =====================================================

-- Criar o schema se não existir
CREATE SCHEMA IF NOT EXISTS `cli_gastos` 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE `cli_gastos`;

-- =====================================================
-- TABELA: contas_bancarias
-- Armazena informações das contas bancárias
-- =====================================================
CREATE TABLE IF NOT EXISTS `contas_bancarias` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(100) NOT NULL UNIQUE,
    `banco` VARCHAR(100) NOT NULL,
    `saldo_atual` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `data_criacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `data_atualizacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABELA: historico_saldo
-- Armazena o histórico de movimentações das contas
-- =====================================================
CREATE TABLE IF NOT EXISTS `historico_saldo` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `conta_id` INT NOT NULL,
    `data_movimentacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `saldo_anterior` DECIMAL(15, 2) NOT NULL,
    `saldo_novo` DECIMAL(15, 2) NOT NULL,
    `valor_movimentacao` DECIMAL(15, 2) NOT NULL,
    `operacao` VARCHAR(255) NOT NULL,
    FOREIGN KEY (`conta_id`) REFERENCES `contas_bancarias`(`id`) ON DELETE CASCADE,
    INDEX `idx_conta_data` (`conta_id`, `data_movimentacao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABELA: despesas
-- Armazena as despesas registradas
-- =====================================================
CREATE TABLE IF NOT EXISTS `despesas` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `descricao` VARCHAR(255) NOT NULL,
    `valor` DECIMAL(15, 2) NOT NULL,
    `categoria` VARCHAR(100) NOT NULL,
    `data_vencimento` DATE NOT NULL,
    `pago` BOOLEAN NOT NULL DEFAULT FALSE,
    `data_pagamento` DATETIME NULL,
    `mes` INT NOT NULL,
    `ano` INT NOT NULL,
    `conta_id` INT NULL,
    `data_criacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `data_atualizacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`conta_id`) REFERENCES `contas_bancarias`(`id`) ON DELETE SET NULL,
    INDEX `idx_mes_ano` (`mes`, `ano`),
    INDEX `idx_categoria` (`categoria`),
    INDEX `idx_pago` (`pago`),
    INDEX `idx_data_vencimento` (`data_vencimento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABELA: receitas
-- Armazena as receitas registradas
-- =====================================================
CREATE TABLE IF NOT EXISTS `receitas` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `descricao` VARCHAR(255) NOT NULL,
    `valor` DECIMAL(15, 2) NOT NULL,
    `categoria` VARCHAR(100) NOT NULL,
    `data_recebimento` DATE NOT NULL,
    `mes` INT NOT NULL,
    `ano` INT NOT NULL,
    `conta_id` INT NULL,
    `data_criacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `data_atualizacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`conta_id`) REFERENCES `contas_bancarias`(`id`) ON DELETE SET NULL,
    INDEX `idx_mes_ano` (`mes`, `ano`),
    INDEX `idx_categoria` (`categoria`),
    INDEX `idx_data_recebimento` (`data_recebimento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABELA: metas_gastos
-- Armazena as metas de gastos por categoria
-- =====================================================
CREATE TABLE IF NOT EXISTS `metas_gastos` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `categoria` VARCHAR(100) NOT NULL,
    `limite_mensal` DECIMAL(15, 2) NOT NULL,
    `gasto_atual` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `mes` INT NOT NULL,
    `ano` INT NOT NULL,
    `alertas_enviados` JSON NULL,
    `data_criacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `data_atualizacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_categoria_mes_ano` (`categoria`, `mes`, `ano`),
    INDEX `idx_mes_ano` (`mes`, `ano`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABELA: configuracoes
-- Armazena configurações do sistema
-- =====================================================
CREATE TABLE IF NOT EXISTS `configuracoes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `chave` VARCHAR(100) NOT NULL UNIQUE,
    `valor` TEXT NOT NULL,
    `descricao` VARCHAR(255) NULL,
    `data_criacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `data_atualizacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_chave` (`chave`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- DADOS INICIAIS
-- =====================================================

-- Inserir conta padrão (Carteira) se não existir
INSERT IGNORE INTO `contas_bancarias` (`nome`, `banco`, `saldo_atual`) 
VALUES ('Carteira', 'Dinheiro em Espécie', 0.00);

-- Inserir conta principal se não existir
INSERT IGNORE INTO `contas_bancarias` (`nome`, `banco`, `saldo_atual`) 
VALUES ('Conta Principal', 'Banco Principal', 0.00);

-- Inserir configuração de conta padrão
INSERT INTO `configuracoes` (`chave`, `valor`, `descricao`) 
VALUES ('conta_padrao', 'Carteira', 'Nome da conta bancária padrão do sistema')
ON DUPLICATE KEY UPDATE `valor` = 'Carteira';

-- =====================================================
-- VIEWS ÚTEIS
-- =====================================================

-- View: Resumo de contas bancárias
CREATE OR REPLACE VIEW `v_resumo_contas` AS
SELECT 
    cb.id,
    cb.nome,
    cb.banco,
    cb.saldo_atual,
    COUNT(DISTINCT hs.id) as total_movimentacoes,
    cb.data_criacao,
    cb.data_atualizacao
FROM `contas_bancarias` cb
LEFT JOIN `historico_saldo` hs ON cb.id = hs.conta_id
GROUP BY cb.id, cb.nome, cb.banco, cb.saldo_atual, cb.data_criacao, cb.data_atualizacao;

-- View: Resumo de despesas por mês/ano
CREATE OR REPLACE VIEW `v_resumo_despesas_mensal` AS
SELECT 
    mes,
    ano,
    COUNT(*) as total_despesas,
    SUM(valor) as valor_total,
    SUM(CASE WHEN pago = TRUE THEN valor ELSE 0 END) as valor_pago,
    SUM(CASE WHEN pago = FALSE THEN valor ELSE 0 END) as valor_pendente,
    COUNT(CASE WHEN pago = TRUE THEN 1 END) as despesas_pagas,
    COUNT(CASE WHEN pago = FALSE THEN 1 END) as despesas_pendentes
FROM `despesas`
GROUP BY mes, ano
ORDER BY ano DESC, mes DESC;

-- View: Resumo de receitas por mês/ano
CREATE OR REPLACE VIEW `v_resumo_receitas_mensal` AS
SELECT 
    mes,
    ano,
    COUNT(*) as total_receitas,
    SUM(valor) as valor_total
FROM `receitas`
GROUP BY mes, ano
ORDER BY ano DESC, mes DESC;

-- View: Gastos por categoria
CREATE OR REPLACE VIEW `v_gastos_por_categoria` AS
SELECT 
    categoria,
    mes,
    ano,
    COUNT(*) as total_despesas,
    SUM(valor) as valor_total,
    SUM(CASE WHEN pago = TRUE THEN valor ELSE 0 END) as valor_pago
FROM `despesas`
GROUP BY categoria, mes, ano
ORDER BY ano DESC, mes DESC, valor_total DESC;

-- View: Despesas vencendo (próximos 7 dias)
CREATE OR REPLACE VIEW `v_despesas_vencendo` AS
SELECT 
    id,
    descricao,
    valor,
    categoria,
    data_vencimento,
    DATEDIFF(data_vencimento, CURDATE()) as dias_para_vencimento,
    mes,
    ano
FROM `despesas`
WHERE pago = FALSE 
    AND data_vencimento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
ORDER BY data_vencimento ASC;

-- View: Metas e gastos atuais
CREATE OR REPLACE VIEW `v_metas_status` AS
SELECT 
    mg.id,
    mg.categoria,
    mg.limite_mensal,
    mg.gasto_atual,
    mg.mes,
    mg.ano,
    ROUND((mg.gasto_atual / mg.limite_mensal) * 100, 2) as percentual_usado,
    CASE 
        WHEN mg.gasto_atual >= mg.limite_mensal THEN 'EXCEDIDA'
        WHEN (mg.gasto_atual / mg.limite_mensal) >= 0.8 THEN 'ALERTA'
        ELSE 'OK'
    END as status_meta
FROM `metas_gastos` mg
ORDER BY percentual_usado DESC;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

-- Procedure: Atualizar gastos das metas
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS `sp_atualizar_gastos_metas`(
    IN p_mes INT,
    IN p_ano INT
)
BEGIN
    -- Atualizar gastos atuais de todas as metas do mês
    UPDATE `metas_gastos` mg
    SET mg.gasto_atual = (
        SELECT COALESCE(SUM(d.valor), 0)
        FROM `despesas` d
        WHERE d.categoria = mg.categoria
            AND d.mes = p_mes
            AND d.ano = p_ano
            AND d.pago = TRUE
    )
    WHERE mg.mes = p_mes AND mg.ano = p_ano;
END$$

DELIMITER ;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Atualizar gastos da meta ao pagar despesa
DELIMITER $$

CREATE TRIGGER IF NOT EXISTS `trg_despesa_paga_atualizar_meta`
AFTER UPDATE ON `despesas`
FOR EACH ROW
BEGIN
    IF NEW.pago = TRUE AND OLD.pago = FALSE THEN
        -- Atualizar gasto_atual da meta correspondente
        UPDATE `metas_gastos`
        SET gasto_atual = gasto_atual + NEW.valor
        WHERE categoria = NEW.categoria
            AND mes = NEW.mes
            AND ano = NEW.ano;
    END IF;
END$$

DELIMITER ;

-- =====================================================
-- ÍNDICES ADICIONAIS PARA PERFORMANCE
-- =====================================================

-- Índice composto para buscas frequentes
CREATE INDEX IF NOT EXISTS `idx_despesas_busca` 
    ON `despesas` (`categoria`, `mes`, `ano`, `pago`);

CREATE INDEX IF NOT EXISTS `idx_receitas_busca` 
    ON `receitas` (`categoria`, `mes`, `ano`);

-- =====================================================
-- COMENTÁRIOS NAS TABELAS
-- =====================================================

ALTER TABLE `contas_bancarias` 
    COMMENT = 'Armazena informações das contas bancárias do usuário';

ALTER TABLE `historico_saldo` 
    COMMENT = 'Histórico completo de movimentações financeiras das contas';

ALTER TABLE `despesas` 
    COMMENT = 'Registro de todas as despesas do sistema';

ALTER TABLE `receitas` 
    COMMENT = 'Registro de todas as receitas do sistema';

ALTER TABLE `metas_gastos` 
    COMMENT = 'Metas de gastos por categoria e período';

ALTER TABLE `configuracoes` 
    COMMENT = 'Configurações gerais do sistema';

-- =====================================================
-- FIM DAS MIGRAÇÕES
-- =====================================================

SELECT 'Migrações executadas com sucesso!' as status;
SELECT 'Schema cli_gastos criado e configurado!' as info;

