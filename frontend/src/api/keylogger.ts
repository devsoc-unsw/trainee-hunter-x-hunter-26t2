import { apiPost } from './client'

// mirrors LogKeyResponse in backend/routers/keylogger.py. `status` used to be
// here and isn't sent - that was the old in-memory dict's shape.
export interface LogKeyResponse {
    key: string
    // the server's running total for this key, not the frontend's guess
    count: number
    // 1 on every PRESSES_PER_COIN-th press, 0 otherwise. the payout rule lives
    // in the backend; this is how the frontend finds out it fired.
    coins_earned: number
}

export async function logKeyPress(key: string): Promise<LogKeyResponse> {
    return apiPost<LogKeyResponse>('/keylogger/log-key', { key })
}