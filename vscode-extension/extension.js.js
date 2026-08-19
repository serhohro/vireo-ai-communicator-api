// ============================================================
// VIREO VSCode EXTENSION
// Запуск скриптів Vireo з редактора
// ============================================================

const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * Активація плагіна
 */
function activate(context) {
    console.log('🟢 Vireo extension activated!');

    // Реєстрація команди для запуску скрипта
    let disposable = vscode.commands.registerCommand('vireo.runScript', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found!');
            return;
        }

        const document = editor.document;
        if (document.languageId !== 'vireo') {
            vscode.window.showErrorMessage('Current file is not Vireo!');
            return;
        }

        const filePath = document.fileName;
        const fileName = path.basename(filePath);
        
        vscode.window.showInformationMessage(`🚀 Running Vireo script: ${fileName}`);

        // Шлях до Vireo інтерпретатора або компілятора
        const vireoPath = path.join(__dirname, '..', '..', 'vireo_interpreter.py');
        const apiPath = path.join(__dirname, '..', '..', 'api_server.py');

        // Перевіряємо, чи існує інтерпретатор
        if (fs.existsSync(vireoPath)) {
            // Запуск через інтерпретатор
            const command = `python "${vireoPath}" "${filePath}"`;
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    vscode.window.showErrorMessage(`❌ Error: ${error.message}`);
                    return;
                }
                if (stderr) {
                    vscode.window.showErrorMessage(`❌ stderr: ${stderr}`);
                    return;
                }
                // Показуємо результат
                vscode.window.showInformationMessage(`✅ Vireo script executed!`);
                vscode.window.showInformationMessage(stdout);
            });
        } else if (fs.existsSync(apiPath)) {
            // Запуск через API сервер
            const command = `python "${apiPath}" &`;
            vscode.window.showInformationMessage('🌐 Vireo API server starting...');
        } else {
            vscode.window.showErrorMessage('❌ Vireo interpreter or API server not found!');
        }
    });

    context.subscriptions.push(disposable);

    // Показати повідомлення при старті
    vscode.window.showInformationMessage('🟢 Vireo extension is ready! Use Ctrl+Shift+R to run scripts.');
}

/**
 * Деактивація плагіна
 */
function deactivate() {
    console.log('🔴 Vireo extension deactivated.');
}

module.exports = {
    activate,
    deactivate
};