dt = 0.01;
T = 5;
t = 0:dt:T;
N = length(t);

y = dlmread('f14.txt',' ');

%1
figure;
plot(t, y, 'b-', 'LineWidth', 1.5);
grid on;
title('Оригінальна дискретна функція y(t) для варіанту 14');
xlabel('t, c');
ylabel('y(t)');


%2
% --- FFT (вбудована функція)
fft_y_raw = fft(y);                % необроблений спектр
fft_y = fft_y_raw / N;             % нормалізація

freq_axis = (0:N-1) / T;           % частотна вісь

figure;
plot(freq_axis, abs(fft_y), 'b-', 'LineWidth', 1.2);
grid on;
title('Амплітудний спектр |C_y(f)| (вбудована FFT)');
xlabel('f, Гц');
ylabel('|C_y(f)|');

% --- Ручна реалізація ДПФ
fft_manual = zeros(1, N);
for k = 1:N
    for m = 1:N
        fft_manual(k) = fft_manual(k) + y(m) * exp(-1i * 2*pi*(k-1)*(m-1)/N);
    end
end
fft_manual = fft_manual / N;       % нормалізація

figure;
plot(freq_axis, abs(fft_manual), 'r-', 'LineWidth', 1.2);
grid on;
title('Амплітудний спектр |C_y(f)| (ручна реалізація)');
xlabel('f, Гц');
ylabel('|C_y(f)|');


%3
% --- Перша половина спектра
fft_half_raw = abs(fft_y_raw(1:round(N/2)));

% --- Масив частот
df = 1 / T;
f = 0:df:(N-1)*df;

% --- Пошук піків
[maxima, locs] = findpeaks(fft_half_raw, 'MinPeakHeight', 5);

% --- Графік з піками
figure;
plot(f(1:round(N/2)), abs(fft_y(1:round(N/2))), 'b-', 'LineWidth', 1.5);
grid on;
hold on;
plot(f(locs), maxima / N, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
hold off;
title('Піки амплітудного спектра (перша половина)');
xlabel('f, Гц');
ylabel('|C_y(f)|');

% --- Вивід частот
disp('--- Знайдені пікові частоти ---');
for i = 1:length(locs)
    fprintf('Пік %d: частота %.4f Гц, амплітуда %.4f\n', ...
        i, f(locs(i)), maxima(i)/N);
end


%4
% --- Частота синусоїди
f1 = 20;

% --- Формування матриці системи
s1 = sin(2*pi*f1*t);
A = [t'.^3, t'.^2, t', s1', ones(N,1)];

% --- Розв'язання A*a = y
coeff = A \ y';

disp('--- Знайдені коефіцієнти ---');
fprintf('a1 (t^3): %.6f\n', coeff(1));
fprintf('a2 (t^2): %.6f\n', coeff(2));
fprintf('a3 (t):   %.6f\n', coeff(3));
fprintf('a4*sin:   %.6f\n', coeff(4));
fprintf('a5 const: %.6f\n', coeff(5));

% --- Побудова моделі
y_model = coeff(1)*t.^3 + coeff(2)*t.^2 + coeff(3)*t + coeff(4)*sin(2*pi*f1*t) + coeff(5);

% --- Похибки
SSE = sum((y_model - y).^2);
MSE = SSE / N;
rel_err = sqrt(SSE / sum(y.^2)) * 100;

disp('--- Похибки моделі ---');
fprintf('SSE: %.6f\n', SSE);
fprintf('MSE: %.6f\n', MSE);
fprintf('Відносна похибка: %.4f %%\n', rel_err);

% --- Графік порівняння
figure;
plot(t, y, 'b-', 'LineWidth', 1.5);
hold on;
plot(t, y_model, 'r--', 'LineWidth', 2);
grid on;
legend('Оригінал', 'Модель');
title('Порівняння y(t) та апроксимації y_{model}(t)');
xlabel('t, c');
ylabel('y');
