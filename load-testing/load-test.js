// K6 Load Testing Script for Meridian Ephemeris API
// This script validates the performance targets from PRP 7

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const cacheMisses = new Counter('cache_misses');
const successfulCalculations = new Counter('successful_calculations');

// Test configuration
export const options = {
  scenarios: {
    // Warm-up phase
    warmup: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
    },
    // Load testing phase
    load_test: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '2m', target: 20 },  // Ramp up to 20 users
        { duration: '5m', target: 50 },  // Ramp up to 50 users
        { duration: '5m', target: 50 },  // Hold at 50 users
        { duration: '2m', target: 100 }, // Ramp up to 100 users
        { duration: '3m', target: 100 }, // Hold at 100 users
        { duration: '2m', target: 0 },   // Ramp down
      ],
    },
    // Spike testing
    spike_test: {
      executor: 'constant-vus',
      vus: 200,
      duration: '1m',
      startTime: '15m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<100'], // 95% of requests should be below 100ms
    error_rate: ['rate<0.1'], // Error rate should be below 10%
    http_req_failed: ['rate<0.05'], // Failed requests should be below 5%
  },
};

// Test data generator
function generateTestSubject() {
  const names = ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'];
  const years = [1980, 1985, 1990, 1995, 2000];
  const months = [1, 3, 6, 9, 12];
  const days = [1, 10, 15, 20, 28];
  const hours = [0, 6, 12, 18];
  
  // Major cities coordinates for realistic testing
  const locations = [
    { lat: 40.7128, lng: -74.0060, name: 'New York' },
    { lat: 51.5074, lng: -0.1278, name: 'London' },
    { lat: 35.6762, lng: 139.6503, name: 'Tokyo' },
    { lat: 48.8566, lng: 2.3522, name: 'Paris' },
    { lat: 37.7749, lng: -122.4194, name: 'San Francisco' },
    { lat: 52.5200, lng: 13.4050, name: 'Berlin' },
    { lat: -33.8688, lng: 151.2093, name: 'Sydney' },
    { lat: 55.7558, lng: 37.6176, name: 'Moscow' },
  ];
  
  const location = locations[Math.floor(Math.random() * locations.length)];
  
  return {
    name: names[Math.floor(Math.random() * names.length)],
    datetime: {
      iso_string: `${years[Math.floor(Math.random() * years.length)]}-${
        months[Math.floor(Math.random() * months.length)].toString().padStart(2, '0')
      }-${
        days[Math.floor(Math.random() * days.length)].toString().padStart(2, '0')
      }T${
        hours[Math.floor(Math.random() * hours.length)].toString().padStart(2, '0')
      }:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}:00`
    },
    latitude: { decimal: location.lat },
    longitude: { decimal: location.lng },
    timezone: { name: 'UTC' }
  };
}

// Base URL configuration
const BASE_URL = __ENV.BASE_URL || 'http://meridian-api:8000';

export default function () {
  // Health check
  const healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 50ms': (r) => r.timings.duration < 50,
  });
  
  // Generate test data
  const subject = generateTestSubject();
  
  // Test natal chart calculation
  const payload = JSON.stringify({
    subject: subject,
    settings: {
      house_system: ['placidus', 'koch', 'equal'][Math.floor(Math.random() * 3)]
    }
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const startTime = Date.now();
  const response = http.post(`${BASE_URL}/ephemeris/natal`, payload, params);
  const endTime = Date.now();
  
  const responseTimeMs = endTime - startTime;
  responseTime.add(responseTimeMs);
  
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 100ms': (r) => r.timings.duration < 100,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'response has success field': (r) => {
      try {
        const json = JSON.parse(r.body);
        return json.hasOwnProperty('success');
      } catch (e) {
        return false;
      }
    },
    'calculation succeeded': (r) => {
      try {
        const json = JSON.parse(r.body);
        return json.success === true;
      } catch (e) {
        return false;
      }
    },
    'has planetary positions': (r) => {
      try {
        const json = JSON.parse(r.body);
        return json.success && json.data && json.data.planets;
      } catch (e) {
        return false;
      }
    },
    'has house data': (r) => {
      try {
        const json = JSON.parse(r.body);
        return json.success && json.data && json.data.houses;
      } catch (e) {
        return false;
      }
    }
  });
  
  if (success) {
    successfulCalculations.add(1);
    
    // Check if this was a cache hit by examining response headers or timing
    if (response.timings.duration < 10) {
      // Likely a cache hit - very fast response
    } else {
      cacheMisses.add(1);
    }
  } else {
    errorRate.add(1);
  }
  
  // Test batch processing endpoint occasionally
  if (Math.random() < 0.1) { // 10% of requests test batch processing
    const batchSize = Math.floor(Math.random() * 10) + 5; // 5-14 subjects
    const batchSubjects = [];
    
    for (let i = 0; i < batchSize; i++) {
      batchSubjects.push(generateTestSubject());
    }
    
    const batchPayload = JSON.stringify({
      subjects: batchSubjects,
      settings: { house_system: 'placidus' }
    });
    
    const batchResponse = http.post(`${BASE_URL}/ephemeris/batch`, batchPayload, params);
    
    check(batchResponse, {
      'batch status is 200': (r) => r.status === 200,
      'batch response time reasonable': (r) => r.timings.duration < (batchSize * 100), // 100ms per chart
      'batch has results': (r) => {
        try {
          const json = JSON.parse(r.body);
          return json.success && json.data && Array.isArray(json.data.results);
        } catch (e) {
          return false;
        }
      },
    });
  }
  
  // Random sleep to simulate realistic user behavior
  sleep(Math.random() * 2 + 0.5); // Sleep 0.5-2.5 seconds
}

// Setup function
export function setup() {
  console.log('🚀 Starting Meridian Ephemeris load test');
  console.log(`📊 Target: ${BASE_URL}`);
  
  // Verify API is available
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`API health check failed: ${healthCheck.status}`);
  }
  
  console.log('✅ API health check passed');
  return {};
}

// Teardown function
export function teardown(data) {
  console.log('📈 Load test completed');
  
  // Get final metrics
  const metricsResponse = http.get(`${BASE_URL}/metrics`);
  if (metricsResponse.status === 200) {
    console.log('📊 Final metrics collected');
  }
}

// Helper function to validate performance targets
export function handleSummary(data) {
  return {
    'summary.json': JSON.stringify(data),
    stdout: `
🎯 Performance Target Validation:
=================================

📊 Request Statistics:
  - Total Requests: ${data.metrics.http_reqs.values.count}
  - Failed Requests: ${data.metrics.http_req_failed.values.rate * 100}%
  - Average Response Time: ${data.metrics.http_req_duration.values.avg}ms
  - 95th Percentile: ${data.metrics.http_req_duration.values['p(95)']}ms
  - 99th Percentile: ${data.metrics.http_req_duration.values['p(99)']}ms

✅ Target Validation:
  - Sub-100ms median: ${data.metrics.http_req_duration.values.med < 100 ? '✅ PASS' : '❌ FAIL'}
  - <5% error rate: ${data.metrics.http_req_failed.values.rate < 0.05 ? '✅ PASS' : '❌ FAIL'}
  - 95th percentile <100ms: ${data.metrics.http_req_duration.values['p(95)'] < 100 ? '✅ PASS' : '❌ FAIL'}

🚀 Performance Summary:
  - Peak Throughput: ${data.metrics.http_reqs.values.rate} req/s
  - Successful Calculations: ${data.metrics.successful_calculations ? data.metrics.successful_calculations.values.count : 'N/A'}
  - Cache Efficiency: ${data.metrics.cache_misses ? (1 - data.metrics.cache_misses.values.count / data.metrics.http_reqs.values.count) * 100 : 'N/A'}%
`,
  };
}