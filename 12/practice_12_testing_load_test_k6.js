import http from 'k6/http';
import { check, sleep } from 'k6';

// 12.2. Конфигурация нагрузочного теста: 50 виртуальных пользователей (VU), 30 секунд
export const options = {
    vus: 50,
    duration: '30s',
    thresholds: {
        http_req_failed: ['rate<0.01'], // Ошибок должно быть меньше 1%
        http_req_duration: ['p(95)<500'], // 95% запросов должны выполняться быстрее 500мс
    },
};

export default function () {
    const url = 'http://localhost:8080/api/v1/products';
    
    // Выполнение GET запроса
    const res = http.get(url);
    
    // Проверка корректности ответа
    check(res, {
        'status is 200': (r) => r.status === 200,
        'transaction time OK': (r) => r.timings.duration < 500,
    });
    
    // Пауза между итерациями для симуляции реального пользователя
    sleep(1);
}
