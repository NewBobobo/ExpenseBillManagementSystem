/**
 * 侧边栏菜单配置
 * 对应 08-feature-spec 菜单结构与页面权限矩阵。
 * roles 为空 = 所有登录用户可见；'admin' = 管理员；'superAdmin' = 顶级机构管理员。
 *
 * 注：W1 仅工作台、机构管理已落地路由；其余项随排期补齐，
 * 暂以 disabled 标记占位，避免点击进入空白路由。
 */
export interface MenuItem {
  /** 路由 path（绝对路径） */
  index: string
  title: string
  /** Element Plus 图标组件名 */
  icon?: string
  roles?: Array<'admin' | 'superAdmin'>
  /** 占位未实现（本阶段尚无路由），渲染为禁用项 */
  disabled?: boolean
  children?: MenuItem[]
}

export const MENU: MenuItem[] = [
  { index: '/dashboard', title: '工作台', icon: 'Monitor' },
  {
    index: 'group-reports',
    title: '费用单管理',
    icon: 'Document',
    children: [
      { index: '/reports/create', title: '填报费用单', disabled: true },
      { index: '/reports', title: '单据列表', disabled: true },
    ],
  },
  {
    index: 'group-basedata',
    title: '基础数据',
    icon: 'Files',
    children: [
      { index: '/expense-items', title: '费用项字典', disabled: true },
      { index: '/seals', title: '公章管理', disabled: true },
    ],
  },
  {
    index: 'group-templates',
    title: '模板管理',
    icon: 'Printer',
    children: [
      { index: '/templates', title: '模板列表', disabled: true },
    ],
  },
  {
    index: 'group-org',
    title: '机构管理',
    icon: 'OfficeBuilding',
    roles: ['admin'],
    children: [
      { index: '/orgs', title: '机构树' },
      { index: '/users', title: '用户管理', disabled: true },
    ],
  },
  {
    index: 'group-system',
    title: '系统设置',
    icon: 'Setting',
    roles: ['superAdmin'],
    children: [
      { index: '/system/defaults', title: '默认配置', disabled: true },
    ],
  },
]
