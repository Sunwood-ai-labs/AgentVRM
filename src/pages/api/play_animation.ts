import { NextApiRequest, NextApiResponse } from 'next';
import WebSocket from 'ws';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { animation } = req.body;

  if (!animation) {
    return res.status(400).json({ error: 'Animation parameter is required' });
  }

  // WebSocketサーバーにメッセージを送信
  const wsUrl = process.env.INTERNAL_WS_URL || 'ws://localhost:8080'; // コンテナ間通信用のURLを使用
  const ws = new WebSocket(wsUrl + '?from=api'); // from=apiでAPIクライアントとして接続

  return new Promise((resolve) => {
    ws.onopen = () => {
      const message = JSON.stringify({
        type: 'play_animation',
        name: animation,
      });
      ws.send(message);
      ws.close();
      resolve(res.status(200).json({ success: true, message: `Sent animation command: ${animation}` }));
    };

    ws.onerror = (error) => {
      console.error('WebSocket error in play_animation:', error);
      // エラーメッセージを具体的にする
      resolve(res.status(500).json({ error: 'WebSocket connection failed. Is the ws-server container running?', details: error.message }));
    };

    ws.onclose = () => {
      // onopen と onerror で resolve されるので、ここでは何もしない
    };
  });
}
