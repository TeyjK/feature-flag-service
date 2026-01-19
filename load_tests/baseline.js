import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 100 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<10'],
  },
};

const API_KEY = 'd5913b8bb4675eb03e6b14173664d5f5';
const BASE_URL = 'http://localhost:8000/api/v1';

export default function () {
  const flagId = 'test-api-flag';
  const userId = `user-${Math.floor(Math.random() * 10000)}`;
  
  const params = {
    headers: {
      'X-API-Key': API_KEY,
    },
  };
  
  const res = http.get(
    `${BASE_URL}/flags/${flagId}/evaluate?user_id=${userId}&environment=prod`,
    params
  );

  if (res.status !== 200) {
    console.log(`Error: ${res.status} - ${res.body}`);
  }
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'has flag_id': (r) => JSON.parse(r.body).flag_id === flagId,
    'has enabled field': (r) => 'enabled' in JSON.parse(r.body),
  });
  
  sleep(0.1);
}