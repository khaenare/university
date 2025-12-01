import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.Pipe;
import java.util.Scanner;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Лабораторна робота з курсу "Операційні системи".
 * Варіант: Java, Future + Polling, java.nio.Pipe.
 *
 * Опис:
 * Головний потік (Manager) запускає дві задачі обчислення (Worker-и) f(x) та g(x).
 * Взаємодія відбувається через канали (Pipes).
 * Менеджер використовує "опитування" (polling) для перевірки статусу задач та часу.
 * Реалізовано механізм м'якого переривання (Prompt) з меню.
 */
public class ComputationSystem {

    // Налаштування часу (в мілісекундах)
    private static final int SOFT_TIMEOUT_MS = 5000; // Час до появи меню (5 сек)

    // Флаг для уникнення "гонки" виводу (щоб результат не псував меню)
    private static final AtomicBoolean isPromptActive = new AtomicBoolean(false);

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("=== Система асинхронних обчислень (MacOS/Java NIO) ===");
        System.out.println("Введіть ціле число 'x' для обчислення або 'q' для виходу.");

        // Головний цикл програми (Life cycle loop)
        while (true) {
            System.out.print("\nВведіть x > ");
            String input = scanner.nextLine();

            if (input.trim().equalsIgnoreCase("q")) {
                System.out.println("Завершення роботи.");
                break;
            }

            try {
                int x = Integer.parseInt(input.trim());
                // Запуск сесії обчислень для введеного X
                runComputationSession(x);
            } catch (NumberFormatException e) {
                System.out.println("Помилка: введіть коректне ціле число.");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        scanner.close();
    }

    /**
     * Сесія обчислення. Реалізує логіку Manager та Polling loop.
     */
    private static void runComputationSession(int x) throws IOException, InterruptedException {
        System.out.println("[Manager] Старт обчислень для x = " + x);
        System.out.println("[Manager] Очікування результатів...");

        // 1. Створення каналів (Pipes)
        // Pipe забезпечує односпрямований потік байтів.
        Pipe pipeF = Pipe.open();
        Pipe pipeG = Pipe.open();

        // 2. Створення та запуск задач (Workers)
        // Використовуємо CompletableFuture як абстракцію над потоками виконання.

        // f(x) = x / 2.0 (Ділення, повертає дійсне число)
// Імітація: швидка (1 сек)
        ComputationTask taskF = new ComputationTask("f(x)", x, pipeF.sink(), 1000, val -> val / 2.0);

// g(x) = x^2 + 2x (Поліном)
// Імітація: повільна (6 сек), щоб ми встигли побачити меню Prompt
        ComputationTask taskG = new ComputationTask("g(x)", x, pipeG.sink(), 6000, val -> (val * val) + (2.0 * val));

        CompletableFuture<Void> futureF = CompletableFuture.runAsync(taskF);
        CompletableFuture<Void> futureG = CompletableFuture.runAsync(taskG);

        // Змінні стану
        long startTime = System.currentTimeMillis();
        Double resF = null;
        Double resG = null;
        boolean calculationFinished = false;

        // --- ЦИКЛ ОПИТУВАННЯ (POLLING LOOP) ---
        // Замість future.get() ми крутимось у циклі, перевіряючи статус.
        while (!calculationFinished) {

            // А. Опитування каналів (Non-blocking check)
            // Якщо задача завершена, але результат ще не зчитаний - читаємо.
            if (resF == null && futureF.isDone()) {
                resF = readFromPipe(pipeF.source(), "f(x)");
            }
            if (resG == null && futureG.isDone()) {
                resG = readFromPipe(pipeG.source(), "g(x)");
            }

            // Б. Перевірка на успішне завершення обох задач
            if (resF != null && resG != null) {
                printResult(x, resF, resG);
                calculationFinished = true;
                break;
            }

            // В. Перевірка тайм-ауту для виклику Меню (Prompt)
            long currentTime = System.currentTimeMillis();
            if ((currentTime - startTime) > SOFT_TIMEOUT_MS && !isPromptActive.get()) {

                // Вмикаємо "режим меню", щоб заблокувати зайвий вивід у консоль
                isPromptActive.set(true);

                // Виклик інтерактивного меню
                PromptResult userChoice = showPrompt(resF, resG);

                isPromptActive.set(false);

                // Обробка вибору користувача
                switch (userChoice) {
                    case CONTINUE:
                        System.out.println("[Manager] Продовжуємо очікування...");
                        // Скидаємо лічильник часу, щоб меню не з'явилось миттєво знову
                        startTime = System.currentTimeMillis();
                        break;

                    case CANCEL:
                        System.out.println("[Manager] Скасування...");
                        // Скасовуємо задачі
                        futureF.cancel(true);
                        futureG.cancel(true);
                        printCancellationSummary(resF, resG);
                        calculationFinished = true;
                        break;
                }
            }

            // Г. Sleep для розвантаження процесора (щоб не було 100% CPU usage)
            Thread.sleep(100);
        }

        // Закриття ресурсів (важливо для MacOS/Linux, щоб не втрачати дескриптори файлів)
        try {
            pipeF.sink().close(); pipeF.source().close();
            pipeG.sink().close(); pipeG.source().close();
        } catch (IOException e) {
            // Ігноруємо помилки закриття при завершенні
        }
    }

    // --- Допоміжні методи та класи ---

    private enum PromptResult { CONTINUE, CANCEL }

    /**
     * Меню користувача (вимога з Відео 2).
     */
    private static PromptResult showPrompt(Double resF, Double resG) {
        Scanner promptScanner = new Scanner(System.in);
        System.out.println("\n\n>>> УВАГА: Час очікування вийшов.");

        while (true) {
            System.out.println("Оберіть дію:");
            System.out.println(" 1. Continue (Продовжити)");
            System.out.println(" 2. Status   (Показати статус)");
            System.out.println(" 3. Cancel   (Скасувати обчислення)");
            System.out.print("> ");

            String line = promptScanner.nextLine().trim();

            if (line.equals("1")) {
                return PromptResult.CONTINUE;
            } else if (line.equals("3")) {
                return PromptResult.CANCEL;
            } else if (line.equals("2")) {
                System.out.println("\n--- ПОТОЧНИЙ СТАТУС ---");
                System.out.println(" f(x): " + (resF != null ? "Готово (" + resF + ")" : "Обчислюється..."));
                System.out.println(" g(x): " + (resG != null ? "Готово (" + resG + ")" : "Обчислюється..."));
                System.out.println("-----------------------");
            } else {
                System.out.println("Невідома команда. Спробуйте ще раз.");
            }
        }
    }

    /**
     * Читання double з каналу Pipe.
     */
    private static Double readFromPipe(Pipe.SourceChannel source, String name) {
        try {
            ByteBuffer buffer = ByteBuffer.allocate(8); // double займає 8 байт
            int bytesRead = source.read(buffer);

            if (bytesRead != -1) {
                buffer.flip(); // Перемикання буфера в режим читання
                if (buffer.remaining() >= 8) {
                    double val = buffer.getDouble();
                    // Виводимо повідомлення, тільки якщо не активно меню
                    if (!isPromptActive.get()) {
                        System.out.println("[Pipe] Отримано результат від " + name + ": " + val);
                    }
                    return val;
                }
            }
        } catch (IOException e) {
            System.err.println("Помилка читання каналу " + name);
        }
        return null;
    }

    private static void printResult(int x, double f, double g) {
        // ВАЖЛИВО: Використовуємо суму (+), як сказано у відео про "суму дійсних"
        double result = f + g;

        System.out.println("\n ОБЧИСЛЕННЯ ЗАВЕРШЕНО");
        System.out.printf("f(%d) = %.4f\n", x, f);
        System.out.printf("g(%d) = %.4f\n", x, g);
        System.out.printf("RESULT (Sum): %.4f\n", result);
    }

    private static void printCancellationSummary(Double f, Double g) {
        System.out.println("\n ОБЧИСЛЕННЯ СКАСОВАНО");
        System.out.println("Результат: UNDEFINED (Невизначено)");
        System.out.println("Причина: Скасування користувачем.");
        System.out.println("Отримані дані:");
        System.out.println(" f(x): " + (f != null ? f.toString() : "немає результату"));
        System.out.println(" g(x): " + (g != null ? g.toString() : "немає результату"));
    }

    /**
     * Клас Worker-а. Виконує обчислення та пише результат у Pipe.
     */
    static class ComputationTask implements Runnable {
        private final String name;
        private final int x;
        private final Pipe.SinkChannel sink;
        private final int delayMs;
        private final java.util.function.Function<Integer, Double> logic;

        public ComputationTask(String name, int x, Pipe.SinkChannel sink, int delayMs, java.util.function.Function<Integer, Double> logic) {
            this.name = name;
            this.x = x;
            this.sink = sink;
            this.delayMs = delayMs;
            this.logic = logic;
        }

        @Override
        public void run() {
            try {
                // Імітація тривалих обчислень
                Thread.sleep(delayMs);

                // Виконання функції
                double res = logic.apply(x);

                // Запис результату в Pipe
                ByteBuffer buffer = ByteBuffer.allocate(8);
                buffer.putDouble(res);
                buffer.flip();

                while (buffer.hasRemaining()) {
                    sink.write(buffer);
                }

                // Важливо: ми не закриваємо канал тут, це робить менеджер.

            } catch (InterruptedException e) {
                // Потік перервано (стандартна обробка скасування)
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}