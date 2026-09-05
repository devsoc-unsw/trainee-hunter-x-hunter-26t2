import { apiPost } from './client'

export interface LogKeyResponse {
    status: string
    key: string
    count: number
    coins_earned: number
}

export async function logKeyPress(key: string): Promise<LogKeyResponse> {
    return apiPost<LogKeyResponse>('/keylogger/log-key', { key })
}