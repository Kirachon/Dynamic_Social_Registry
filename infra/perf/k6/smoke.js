import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<500']
  }
};

export default function () {
  const res = http.get('http://localhost:8002/health');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}

