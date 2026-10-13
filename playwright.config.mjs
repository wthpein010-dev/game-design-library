import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests/browser',use:{baseURL:'http://127.0.0.1:8767',headless:true},webServer:{command:'python -m http.server 8767 --bind 127.0.0.1 --directory site',url:'http://127.0.0.1:8767',reuseExistingServer:!process.env.CI},reporter:'list'});
