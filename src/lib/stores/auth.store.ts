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
    if (!username || !password) {
      throw new Error('用户名和密码不能为空');
    }

    try {
      // 清除现有状态
      authStore.set(initialState);
      localStorage.removeItem('authToken');

      // 获取JWT token
      const loginResponse = await fetch('/api/v1/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          username,
          password
        })
      });

      if (!loginResponse.ok) {
        throw new Error(`登录失败: ${loginResponse.status}`);
      }

      const loginResult = await loginResponse.json();
      // 更灵活的token提取逻辑，支持多种常见token字段名
      // 更严格的token提取和验证
      let token = loginResult.access_token || loginResult.token || 
                 loginResult.data?.token || loginResult.data?.access_token;
      if (!token || typeof token !== 'string') {
        throw new Error('未收到有效的token');
      }
      
      // 清理token格式，移除可能的Bearer前缀
      token = token.replace(/^Bearer\s+/i, '').trim();
      if (!token) {
        throw new Error('无效的token格式');
      }

      // 验证token并获取用户信息
      const response = await fetch('/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`获取用户信息失败: ${response.status}`);
      }

      const result = await response.json();
      const userData = result.data || result;
      
      if (!userData || !userData.id) {
        throw new Error('无效的用户数据');
      }

      // 确保token是字符串类型
      const validToken = typeof token === 'string' ? token : String(token);
      
      // 更新状态和本地存储
      authStore.update(state => ({
        ...state,
        isAuthenticated: true,
        token: validToken,
        user: {
          id: userData.id,
          username: userData.username || userData.name || '',
          email: userData.email || ''
        }
      }));
      
      // 确保localStorage操作成功
      try {
        localStorage.setItem('authToken', validToken);
        console.log('Token stored successfully:', validToken);
      } catch (err) {
        console.error('Failed to store token:', err);
      }
      return true;
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

export async function refreshToken(): Promise<boolean> {
    try {
        console.log('尝试刷新token...');
        const response = await fetch('/api/v1/users/refresh', {
            method: 'POST',
            credentials: 'include'
        });
        
        if (!response.ok) {
            console.log('刷新token请求失败:', response.status);
            return false;
        }
        
        const result = await response.json();
        let token = result.access_token || result.token || 
                  result.data?.token || result.data?.access_token;
        if (!token) {
            console.log('未收到有效的token');
            return false;
        }
        
        // 清理token格式，移除可能的Bearer前缀
        token = token.replace(/^Bearer\s+/i, '').trim();
        if (!token) {
            console.log('无效的token格式');
            return false;
        }

        console.log('成功刷新token:', token);
        authStore.update(state => ({
            ...state,
            token
        }));
        
        try {
            localStorage.setItem('authToken', token);
            console.log('Token存储成功');
        } catch (err) {
            console.error('存储token失败:', err);
        }
        return true;
    } catch (err) {
        console.error('刷新token失败:', err);
        return false;
    }
}

  export async function initializeAuth() {
    let token: string | null = null;
    try {
      token = localStorage.getItem('authToken');
      console.log('Retrieved token from localStorage:', token);
      
      // 基本token验证
      if (!token || typeof token !== 'string') {
        authStore.set(initialState);
        localStorage.removeItem('authToken');
        return false;
      }
      
      // 清理token格式，移除可能的Bearer前缀
      token = token.replace(/^Bearer\s+/i, '').trim();
      if (!token) {
        authStore.set(initialState);
        localStorage.removeItem('authToken');
        return false;
      }
    } catch (err) {
      console.error('Failed to read token from localStorage:', err);
      authStore.set(initialState);
      return false;
    }

    try {
      // 验证token有效性
      const response = await fetch('/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
      });

      if (!response.ok) {
        if (response.status === 401) {
          console.log('Token验证失败，尝试刷新');
          const refreshed = await refreshToken();
          if (refreshed) {
            return await initializeAuth(); // 重试初始化
          }
          console.log('刷新token失败，保持当前状态');
          return false; // 不抛出错误，保持当前状态
        }
        throw new Error(`Token验证失败: ${response.status}`);
      }

      const result = await response.json();
      const userData = result.data || result;
      
      if (!userData || !userData.id) {
        throw new Error('无效的用户数据');
      }

      authStore.update(state => ({
        ...state,
        isAuthenticated: true,
        token,
        user: {
          id: userData.id,
          username: userData.username || userData.name || '',
          email: userData.email || ''
        }
      }));
      return true;
    } catch (err) {
      console.error('初始化认证失败:', err);
      authStore.set(initialState);
      localStorage.removeItem('authToken');
      return false;
    }
}
