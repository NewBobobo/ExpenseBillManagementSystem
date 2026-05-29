# 模板 XML 规范

## 概述

模板采用 XML 格式定义单据的打印样式。每个机构可维护多套模板,支持导入导出。
前端解析 XML 渲染 HTML 预览,后端解析 XML 生成 PDF/Excel。

## XML 结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<template name="标准版" version="1.0">

  <!-- 页面设置 -->
  <page size="A4" orientation="portrait" margin-top="20" margin-bottom="20"
        margin-left="15" margin-right="15" unit="mm"/>

  <!-- 表头区域 -->
  <header>
    <logo position="left" x="15" y="10" width="60" height="60"/>
    <title align="center" font-size="22" font-weight="bold" y="20">
      {{org.name}} 费用单
    </title>
    <fields layout="right" y="50">
      <field label="单号" value="{{report.code}}"/>
      <field label="日期" value="{{report.report_date}}"/>
    </fields>
  </header>

  <!-- 明细表格 -->
  <body>
    <table border="1" font-size="12" header-bg="#f5f5f5" y="80">
      <columns>
        <column key="seq"        title="序号"     width="8%"  align="center"/>
        <column key="name"       title="费用名称" width="34%" align="left"/>
        <column key="qty"        title="数量"     width="14%" align="center"/>
        <column key="unit_price" title="单价"     width="20%" align="right"/>
        <column key="amount"     title="金额"     width="24%" align="right"/>
      </columns>
      <rows from="report.items"/>
    </table>

    <!-- 合计 -->
    <summary y-offset="10">
      <field label="合计" value="{{report.total_amount}}" prefix="¥"
             align="right" font-size="14" font-weight="bold"/>
      <field label="大写" value="{{report.total_cn}}" align="right"/>
    </summary>
  </body>

  <!-- 表尾区域 -->
  <footer>
    <field label="收单据方" value="{{report.recipient}}" x="15" y="0"/>
    <field label="填报人" value="{{report.reporter}}" x="15" y="25"/>
    <seal x="420" y="-30" width="100" height="100" rotation="-5" opacity="0.85"/>
  </footer>

</template>
```

## 占位符语法

| 占位符 | 数据来源 |
|--------|----------|
| `{{org.name}}` | 当前机构名称 |
| `{{org.code}}` | 当前机构编号 |
| `{{report.code}}` | 单据编号 |
| `{{report.report_date}}` | 单据日期 |
| `{{report.recipient}}` | 收单据方 |
| `{{report.reporter}}` | 填报人姓名 |
| `{{report.total_amount}}` | 合计金额(数字) |
| `{{report.total_cn}}` | 合计金额(中文大写) |
| `{{report.items}}` | 明细行数组 |
| `{{report.remark}}` | 备注 |

## 元素属性说明

### page 元素

| 属性 | 说明 | 可选值 |
|------|------|--------|
| size | 纸张大小 | A4, A5, B5 |
| orientation | 方向 | portrait(纵向), landscape(横向) |
| margin-* | 边距(mm) | 数字 |

### logo 元素

| 属性 | 说明 |
|------|------|
| x, y | 位置坐标(mm) |
| width, height | 尺寸(mm) |
| position | 快捷定位:left / center / right |

### seal 元素

| 属性 | 说明 |
|------|------|
| x, y | 位置坐标(mm) |
| width, height | 尺寸(mm) |
| rotation | 旋转角度(度),模拟真实盖章效果 |
| opacity | 透明度(0-1) |

### column 元素

| 属性 | 说明 |
|------|------|
| key | 数据字段名 |
| title | 列标题显示文字 |
| width | 列宽(百分比) |
| align | 对齐:left / center / right |

## 模板导入导出

- 导出:GET `/api/templates/{id}/xml` 返回 XML 文件下载
- 导入:POST `/api/templates` 上传 XML 文件,解析后存入数据库
- 校验:导入时校验 XML 结构完整性,缺失必要元素时返回错误提示

## 前端渲染流程

1. 前端从接口获取模板 XML 字符串
2. 使用 DOMParser 解析为 DOM 树
3. 遍历节点,映射为 HTML 元素 + CSS 样式
4. 替换占位符为实际数据(或 mock 数据)
5. 渲染为实时预览(iframe 或 shadow DOM)

## 后端 PDF 生成流程

1. 从数据库读取模板 XML
2. 解析 XML,结合单据数据替换占位符
3. 生成完整 HTML(含内联 CSS + Base64 图片)
4. Playwright 打开 HTML,设置纸张参数,输出 PDF
5. 返回 PDF 文件流
