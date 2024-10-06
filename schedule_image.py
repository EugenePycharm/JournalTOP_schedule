from PIL import Image, ImageDraw, ImageFont

def generate_schedule_image(data, output_path='raspisanie_beautiful.jpg'):
    # Создаем изображение
    img = Image.new('RGB', (1350, 400), 'white')
    draw = ImageDraw.Draw(img)

    # Шрифт для заголовка и текста
    font_header = ImageFont.truetype('C:\\Users\\eugene\\AppData\\Local\\Microsoft\\Windows\\Fonts\\dodo.ttf', 24)
    font_text = ImageFont.truetype('C:\\Users\\eugene\\AppData\\Local\\Microsoft\\Windows\\Fonts\\dodo.ttf', 16)

    # Цвета
    header_color = (70, 130, 180)
    text_color = (0, 0, 0)
    cell_bg_color = (240, 248, 255)
    border_color = (169, 169, 169)

    # Размеры ячеек
    cell_widths = [150, 100, 150, 300, 400, 150]
    cell_height = 60

    # Позиции и отступы
    start_x, start_y = 50, 50
    padding = 10

    # Заголовки
    headers = ["Дата", "Пара", "Время", "Препод", "Предмет", "Аудитория"]

    # Рисуем заголовки таблицы
    for i, header in enumerate(headers):
        x = start_x + sum(cell_widths[:i])
        y = start_y
        draw.rectangle([x, y, x + cell_widths[i], y + cell_height], fill=header_color, outline=border_color)
        draw.text((x + padding, y + padding), header, font=font_header, fill='white')

    # Рисуем строки с данными
    for row_idx, lesson in enumerate(data):
        for col_idx, key in enumerate(['date', 'lesson', 'started_at', 'teacher_name', 'subject_name', 'room_name']):
            x = start_x + sum(cell_widths[:col_idx])
            y = start_y + (row_idx + 1) * cell_height

            # Определяем значение ячейки
            if key == 'lesson':
                cell_text = f"Пара {lesson[key]}"
            elif key == 'started_at':
                cell_text = f"{lesson['started_at']} - {lesson['finished_at']}"
            else:
                cell_text = lesson[key]

            # Рисуем фон ячейки
            draw.rectangle([x, y, x + cell_widths[col_idx], y + cell_height], fill=cell_bg_color if row_idx % 2 == 0 else 'white', outline=border_color)

            # Печатаем текст
            draw.text((x + padding, y + padding), cell_text, font=font_text, fill=text_color)

    # Сохраняем изображение
    img.save(output_path)
    return output_path
