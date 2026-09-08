// ============================================================
// STANDARD LIBRARY: I/O OPERATIONS
// ============================================================
// Version: 3.0.0
// ============================================================

// ============================================================
// ФАЙЛИ
// ============================================================

// Читання файлу
fn read_file(path) {
    return File.read(path)
}

// Читання текстового файлу
fn read_text(path) {
    return File.read_text(path)
}

// Читання байтового файлу
fn read_bytes(path) {
    return File.read_bytes(path)
}

// Запис у файл
fn write_file(path, content) {
    return File.write(path, content)
}

// Запис тексту у файл
fn write_text(path, content) {
    return File.write_text(path, content)
}

// Запис байтів у файл
fn write_bytes(path, content) {
    return File.write_bytes(path, content)
}

// Додавання у файл
fn append_file(path, content) {
    return File.append(path, content)
}

// Перевірка існування файлу
fn file_exists(path) {
    return File.exists(path)
}

// Видалення файлу
fn delete_file(path) {
    return File.delete(path)
}

// Отримання розміру файлу
fn file_size(path) {
    return File.size(path)
}

// Отримання інформації про файл
fn file_info(path) {
    return {
        name: File.name(path),
        size: File.size(path),
        modified: File.modified(path),
        created: File.created(path),
        is_dir: File.is_dir(path)
    }
}

// ============================================================
// ДИРЕКТОРІЇ
// ============================================================

// Список файлів у директорії
fn list_files(path) {
    return File.list(path)
}

// Список файлів з фільтром
fn list_files_filtered(path, pattern) {
    let files = File.list(path)
    let result = []
    for file in files {
        if file.contains(pattern) {
            result.append(file)
        }
    }
    return result
}

// Створення директорії
fn create_dir(path) {
    return File.mkdir(path)
}

// Створення директорії з батьківськими
fn create_dirs(path) {
    return File.mkdirs(path)
}

// Видалення директорії
fn remove_dir(path) {
    return File.rmdir(path)
}

// Видалення директорії рекурсивно
fn remove_dir_recursive(path) {
    return File.rmdir_recursive(path)
}

// ============================================================
// КОНСОЛЬ
// ============================================================

// Читання з консолі
fn read_input(prompt) {
    if prompt != "" {
        print(prompt)
    }
    return input()
}

// Читання рядка
fn read_line() {
    return input()
}

// Читання числа
fn read_number() {
    let line = read_line()
    return to_int(line)
}

// Читання числа з плаваючою точкою
fn read_float() {
    let line = read_line()
    return to_float(line)
}

// ============================================================
// ФОРМАТУВАННЯ
// ============================================================

// Форматування рядка
fn format(template, args) {
    return String.format(template, args)
}

// Форматування з іменованими параметрами
fn format_named(template, params) {
    let result = template
    for key, value in params {
        result = result.replace("{" + key + "}", value)
    }
    return result
}

// ============================================================
// JSON
// ============================================================

// JSON парсинг
fn parse_json(json_str) {
    return JSON.parse(json_str)
}

// JSON генерація
fn to_json(obj) {
    return JSON.stringify(obj)
}

// JSON генерація з форматуванням
fn to_json_pretty(obj) {
    return JSON.stringify(obj, indent=2)
}

// ============================================================
// CSV
// ============================================================

// CSV парсинг
fn parse_csv(csv_str) {
    return CSV.parse(csv_str)
}

// CSV парсинг з заголовками
fn parse_csv_with_headers(csv_str) {
    return CSV.parse_with_headers(csv_str)
}

// CSV генерація
fn to_csv(data) {
    return CSV.stringify(data)
}

// ============================================================
// ТИМЧАСОВІ ФАЙЛИ
// ============================================================

// Створення тимчасового файлу
fn temp_file() {
    return File.temp()
}

// Створення тимчасової директорії
fn temp_dir() {
    return File.temp_dir()
}

// Видалення тимчасового файлу
fn delete_temp(path) {
    return File.delete_temp(path)
}