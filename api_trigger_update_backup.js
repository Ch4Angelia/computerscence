// /api_trigger_update_backup.js

// 注意：此檔案是備份，目的是避免 Vercel 部署時創建 /api/trigger-update.js。
// 若要重新啟用後端功能，請將此內容移回 /api/trigger-update.js，並刪除此備份檔案。

import { VercelRequest, VercelResponse } from '@vercel/node';
import axios from 'axios';

// 從 Vercel 環境變數中讀取密鑰和資訊
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPO = process.env.GITHUB_REPO;
const GITHUB_OWNER = process.env.GITHUB_OWNER;
const GITHUB_URL = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/dispatches`;

export default async (req, res) => {
    // 檢查是否為 POST 請求 (避免惡意或錯誤觸發)
    if (req.method !== 'POST') {
        res.status(405).send('Method Not Allowed');
        return;
    }

    if (!GITHUB_TOKEN || !GITHUB_REPO || !GITHUB_OWNER) {
        console.error('GitHub environment variables are missing!');
        return res.status(500).json({ error: 'Server configuration error: GitHub secrets missing.' });
    }

    try {
        const response = await axios.post(
            GITHUB_URL,
            {
                // 這會觸發 .github/workflows/daily_update.yml 中 on: repository_dispatch 的 trigger_update 事件
                event_type: 'trigger_update',
            },
            {
                headers: {
                    'Authorization': `token ${GITHUB_TOKEN}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json',
                },
            }
        );

        if (response.status === 204) {
            // 204 No Content 代表 GitHub 成功接收指令
            res.status(200).json({ message: 'Update triggered successfully on GitHub Actions.', status: 204 });
        } else {
            // 處理非 204 的響應
            res.status(response.status).json({ error: 'Failed to trigger GitHub Actions.', detail: response.data });
        }
    } catch (error) {
        console.error('Error triggering GitHub Actions:', error.response ? error.response.data : error.message);
        res.status(500).json({ error: 'Internal server error while communicating with GitHub.', detail: error.message });
    }
};