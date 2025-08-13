// K6 Stress Testing Script for Meridian Ephemeris API
// Tests system behavior under extreme load conditions

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('stress_error_rate');
const responseTime = new Trend('stress_response_time');
const systemBreakpoint = new Counter('system_breakpoint');

export const options = {
  scenarios: {
    stress_ramp: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '1m', target: 50 },   // Normal load
        { duration: '2m', target: 100 },  // Above normal
        { duration: '2m', target: 200 },  // Stress level
        { duration: '2m', target: 500 },  // High stress
        { duration: '1m', target: 1000 }, // Extreme stress
        { duration: '2m', target: 1000 }, // Hold extreme
        { duration: '3m', target: 0 },    // Cool down
      ],
    },
  },
  thresholds: {
    stress_error_rate: ['rate<0.3'], // Allow up to 30% errors under stress
    stress_response_time: ['p(95)<1000'], // 95% under 1 second during stress
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://meridian-api:8000';

function generateStressTestData() {
  // Generate more complex/challenging data for stress testing
  return {
    name: `Stress Test User ${Math.random()}`,
    datetime: {
      iso_string: `${1900 + Math.floor(Math.random() * 124)}-${
        (Math.floor(Math.random() * 12) + 1).toString().padStart(2, '0')
      }-${
        (Math.floor(Math.random() * 28) + 1).toString().padStart(2, '0')
      }T${Math.floor(Math.random() * 24).toString().padStart(2, '0')}:${
        Math.floor(Math.random() * 60).toString().padStart(2, '0')
      }:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`
    },
    latitude: { decimal: (Math.random() - 0.5) * 180 }, // Full range
    longitude: { decimal: (Math.random() - 0.5) * 360 }, // Full range
    timezone: { name: 'UTC' }
  };
}

export default function () {
  const subject = generateStressTestData();
  
  const payload = JSON.stringify({
    subject: subject,
    settings: {
      house_system: 'placidus'
    }
  });
  
  const params = {
    headers: { 'Content-Type': 'application/json' },
    timeout: '10s', // Longer timeout for stress testing
  };
  
  const response = http.post(`${BASE_URL}/ephemeris/natal`, payload, params);
  
  responseTime.add(response.timings.duration);
  
  const success = check(response, {
    'status is not 5xx': (r) => r.status < 500,
    'response received': (r) => r.status !== 0,
    'response time < 10s': (r) => r.timings.duration < 10000,
  });
  
  if (!success) {
    errorRate.add(1);
    
    // Detect if system has hit a breaking point
    if (response.status === 0 || response.timings.duration > 10000) {
      systemBreakpoint.add(1);
    }
  }
  
  // Minimal sleep during stress test
  sleep(0.1);
}

export function handleSummary(data) {
  return {
    'stress-summary.json': JSON.stringify(data),
    stdout: `
🔥 Stress Test Results:
======================

📊 Peak Performance:
  - Max Concurrent Users: 1000
  - Total Requests: ${data.metrics.http_reqs.values.count}
  - Peak RPS: ${data.metrics.http_reqs.values.rate}
  - Error Rate: ${data.metrics.stress_error_rate.values.rate * 100}%

⚡ Response Times Under Stress:
  - Average: ${data.metrics.stress_response_time.values.avg}ms
  - 95th Percentile: ${data.metrics.stress_response_time.values['p(95)']}ms
  - 99th Percentile: ${data.metrics.stress_response_time.values['p(99)']}ms

🚨 System Stability:
  - Breakpoint Events: ${data.metrics.system_breakpoint ? data.metrics.system_breakpoint.values.count : 0}
  - System Remained Stable: ${(data.metrics.system_breakpoint ? data.metrics.system_breakpoint.values.count : 0) < 10 ? '✅' : '❌'}

💡 Recommendations:
  ${data.metrics.stress_error_rate.values.rate > 0.1 ? 
    '- Consider increasing system resources or implementing rate limiting' : 
    '- System handled stress well, consider testing higher loads'}
  ${data.metrics.stress_response_time.values['p(95)'] > 500 ? 
    '- Response times degrade under load, optimize critical paths' : 
    '- Response times remain reasonable under stress'}
`,
  };
}