# Actual Data Report — xlsx Schema
# Отчёт фактических данных — схема xlsx

**Artifact:** actual-data-report.xlsx
**Task:** #28 — Collect actual project data (Phase 6 — Closure)
**Артефакт:** actual-data-report.xlsx
**Задача:** #28 — Сбор фактических данных проекта (Фаза 6 — Закрытие)

---

## Sheet / Лист 1: Project Summary / Сводка по проекту

| Column / Столбец | EN | RU | Data type / Тип |
|-----------------|----|----|-----------------|
| A | Parameter | Параметр | Text |
| B | Planned | Плановый | Value |
| C | Actual | Фактический | Value |
| D | Deviation | Отклонение | Formula: =C-B |
| E | Deviation % | Отклонение % | Formula: =D/B*100 |

**Rows / Строки:**
1. Project name / Название проекта
2. Start date / Дата начала
3. End date / Дата завершения
4. Total duration (days) / Общая продолжительность (дн.)
5. Total budget / Общий бюджет
6. Total spent / Фактические затраты
7. Total tasks / Всего задач
8. Tasks completed / Задач выполнено
9. Tasks not completed / Задач не выполнено
10. Total story points / Всего story points
11. Story points delivered / Story points реализовано
12. Number of sprints / Количество спринтов

---

## Sheet / Лист 2: Tasks by Phase / Задачи по фазам

| Column / Столбец | EN | RU | Data type / Тип |
|-----------------|----|----|-----------------|
| A | Phase | Фаза | Text |
| B | Task ID | ID задачи | Text |
| C | Task Name | Название задачи | Text |
| D | Assignee | Исполнитель | Text |
| E | Status | Статус | Text (Done / Not done) |
| F | Planned start | Плановая дата начала | Date |
| G | Planned end | Плановая дата завершения | Date |
| H | Actual start | Фактическая дата начала | Date |
| I | Actual end | Фактическая дата завершения | Date |
| J | Delay (days) | Задержка (дн.) | Formula: =I-G (if done), else "" |
| K | Story points | Story points | Number |
| L | Actual hours | Фактические часы | Number |
| M | Notes | Примечания | Text |

**Data source / Источник:** Jira export (all closed + open tasks) / Выгрузка Jira (все задачи)

---

## Sheet / Лист 3: Budget Breakdown / Детализация бюджета

| Column / Столбец | EN | RU | Data type / Тип |
|-----------------|----|----|-----------------|
| A | Budget category | Статья бюджета | Text |
| B | Planned amount | Плановая сумма | Number |
| C | Actual amount | Фактическая сумма | Number |
| D | Deviation | Отклонение | Formula: =C-B |
| E | Deviation % | Отклонение % | Formula: =D/B*100 |
| F | Notes | Примечания | Text |

**Budget categories (rows) / Статьи бюджета:**
- Personnel / Персонал
- Infrastructure / Инфраструктура
- External services / Внешние сервисы
- Marketing / Маркетинг
- Other / Прочее
- **Total / Итого** (SUM row)

---

## Sheet / Лист 4: Sprint Velocity / Скорость спринтов

| Column / Столбец | EN | RU | Data type / Тип |
|-----------------|----|----|-----------------|
| A | Sprint | Спринт | Text |
| B | Planned story points | Плановые SP | Number |
| C | Completed story points | Выполненные SP | Number |
| D | Velocity % | Скорость % | Formula: =C/B*100 |
| E | Tasks planned | Задач запланировано | Number |
| F | Tasks completed | Задач выполнено | Number |
| G | Notes | Примечания | Text |

**Chart recommendation / Рекомендация:** Add bar chart comparing planned vs actual SP per sprint.
**Рекомендация:** Добавить столбчатую диаграмму план vs факт SP по спринтам.

---

## Formatting Rules / Правила форматирования

| Rule / Правило | Detail / Детали |
|---------------|----------------|
| Header row / Заголовок | Bold, background color #1F4E79, white text |
| Deviation cells > 10% | Red background / Красный фон |
| Deviation cells 5–10% | Yellow background / Жёлтый фон |
| Deviation cells < 5% | No highlight / Без выделения |
| Total rows | Bold |
| Date format | YYYY-MM-DD |
| Number format | 2 decimal places for %, 0 for counts |

---

## PM Instructions / Инструкции PM

**EN:** This file contains the schema structure. To fill it:
1. Export all tasks from Jira (filter: project = {PROJECT_KEY}, all sprints).
2. Paste task data into Sheet 2 (Tasks by Phase).
3. Fill Sheet 3 (Budget) from project-budget.xlsx actuals.
4. Sheet 4 (Sprint Velocity) — fill from Jira sprint reports.
5. Sheet 1 (Summary) — formulas auto-calculate once other sheets are filled.

**RU:** Этот файл содержит схему структуры. Для заполнения:
1. Выгрузи все задачи из Jira (фильтр: проект = {PROJECT_KEY}, все спринты).
2. Вставь данные задач на Лист 2 (Задачи по фазам).
3. Заполни Лист 3 (Бюджет) на основе фактических данных из project-budget.xlsx.
4. Лист 4 (Скорость спринтов) — заполни из отчётов Jira по спринтам.
5. Лист 1 (Сводка) — формулы рассчитываются автоматически после заполнения других листов.
