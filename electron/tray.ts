/*
 * @Author: LiZhiWei
 * @Date: 2025-12-23 14:53:55
 * @LastEditors: LiZhiWei
 * @LastEditTime: 2025-12-24 15:43:17
 * @Description: 
 */
import { app, Tray, Menu, nativeImage } from 'electron'
// import { authStore } from './store'

let tray: Tray | null = null
let trayCallbacks: {
  onQuit: () => void;
  onLogin: () => void;
  onLogout: () => void;
} | null = null

export function createTray(
  iconPath: string,
  callbacks: {
    onQuit: () => void;
    onLogin: () => void;
    onLogout: () => void;
  }
) {
  trayCallbacks = callbacks
  console.log('Creating tray with icon:', iconPath)
  
  // 创建托盘图标
  const icon = nativeImage.createFromPath(iconPath)
  
  if (icon.isEmpty()) {
    console.error('Failed to load tray icon from:', iconPath)
  }

  tray = new Tray(icon.resize({ width: 16, height: 16 }))

  updateTrayMenu()
  tray.setToolTip('小桌宠')
}

export function updateTrayMenu() {
  if (!tray || !trayCallbacks) {
    console.log('Tray or callbacks not initialized yet')
    return
  }

  // const token = authStore.get('token')
  // const isLoggedIn = !!token
  // console.log('Updating tray menu, isLoggedIn:', isLoggedIn)

  const contextMenu = Menu.buildFromTemplate([
    // {
    //   label: isLoggedIn ? '退出登录' : '登录账号',
    //   click: () => {
    //     if (isLoggedIn) {
    //       trayCallbacks?.onLogout()
    //     } else {
    //       trayCallbacks?.onLogin()
    //     }
    //   }
    // },
    // { type: 'separator' },
    {
      label: '开机启动',
      type: 'checkbox',
      checked: app.getLoginItemSettings().openAtLogin,
      click: (menuItem) => {
        app.setLoginItemSettings({
          openAtLogin: menuItem.checked,
          path: process.execPath,
        })
      },
    },
    // 版本号
    {
      label: `版本号: v${app.getVersion()}`,
      enabled: false,
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        trayCallbacks?.onQuit()
      },
    },
  ])

  tray.setContextMenu(contextMenu)
}

// 销毁托盘
export function destroyTray() {
  if (tray) {
    tray.destroy()
    tray = null
  }
}
