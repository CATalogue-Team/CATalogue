import { writable } from 'svelte/store';

export interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    user: {
        id: string;
        username: string;
        email: string;
    } | null;
}

const initialState: AuthState = {
    isAuthenticated: false,
    token: null,
    user: null
};

export const authStore = writable<AuthState>(initialState);

export async function login(username: string, password: string) {
    // 基本验证
    if (!username || !password) {
        throw new Error('用户名和密码不能为空');
    }

    try {
        // 先获取JWT token
        const loginResponse = await fetch('/api/v1/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                password
            })
        });

        if (!loginResponse.ok) {
            throw new Error('登录失败');
        }

        const loginResult = await loginResponse.json();
        const token = loginResult.access_token || loginResult.token;
        if (!token) {
            throw new Error('未收到有效的token');
        }

        // 使用获取的token调用API获取用户信息
        const response = await fetch('/api/v1/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('获取用户信息失败');
        }

        const result = await response.json();
        
        // 验证API返回数据结构
        if (!result || typeof result !== 'object') {
            throw new Error('无效的API响应格式');
        }

        const userData = result.data || result; // 兼容两种响应格式
        
        authStore.update(state => ({
            ...state,
            isAuthenticated: true,
            token,
            user: {
                id: userData.id || '',
                username: userData.username || userData.name || 'user',
                email: userData.email || 'user@example.com'
            }
        }));
        localStorage.setItem('authToken', token);
    } catch (err) {
        console.error('登录失败:', err);
        const message = err instanceof Error ? err.message : '未知错误';
        throw new Error('登录失败: ' + message);
    }
}

export function logout() {
    authStore.set(initialState);
    localStorage.removeItem('authToken');
}

export async function initializeAuth() {
    const token = localStorage.getItem('authToken');
    if (token) {
        // 验证token有效性
        try {
            const response = await fetch('/api/v1/users/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                if (!result || typeof result !== 'object') {
                    throw new Error('无效的API响应格式');
                }
                authStore.update(state => ({
                    ...state,
                    isAuthenticated: true,
                    token,
                    user: {
                        id: result.data?.id || result.id || '',
                        username: result.data?.username || result.username || 'user',
                        email: result.data?.email || result.email || 'user@example.com'
                    }
                }));
                return true;
            }
        } catch (err) {
            console.error('Token验证失败:', err);
            localStorage.removeItem('authToken');
        }
    }
    authStore.set(initialState);
    return false;
}
