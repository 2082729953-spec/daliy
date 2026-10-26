"""Generate public Obsidian reading notes from reports.json; stdlib only.
Generated notes are a read model. Handwritten knowledge is not overwritten.
"""
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
KNOWLEDGE = {
    'K-01-贡献利润': '比较收益时，注明收入是否扣退款，以及佣金、优惠、配送、食材、包装和增量人工的范围；单均与总额同时观察。具体企业口径另行核对。',
    'K-02-转化与履约': '区分曝光、点击、支付、核销或完成履约、退款后成交和复购；比率注明分子、分母、去重单位与时间窗口。',
    'K-03-指标口径与因果': '区分总量、增幅、商家数量和发生概率。报道中的变化不单独证明因果增量；比较前统一范围、基数、窗口和退款口径。',
    'K-04-商家分层与激励': '按商家阶段和经营问题设计服务与任务；工具使用和补贴消耗是过程指标，还需观察留存、经营收益与用户体验。',
    'K-05-商品表达与信任': '内容和商品实际体验需一致；素材评估同时观察点击、支付、退款原因与收益。具体平台规则与地域版本单独保存。',
}


def md(title, kind, body, **props):
    meta = dict(type=kind, title=title, visibility='public', **props)
    return '---\n' + ''.join(k + ': ' + json.dumps(v, ensure_ascii=False) + '\n' for k, v in meta.items()) + '---\n\n# ' + title + '\n\n' + body.strip() + '\n'


def validate(data):
    if not isinstance(data, list) or not data:
        raise ValueError('Refusing empty or non-list archive')
    seen = set()
    for r in data:
        if not isinstance(r, dict):
            raise ValueError('Report must be an object')
        date = r.get('date', '')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date) or date in seen:
            raise ValueError('Invalid or duplicate issue date')
        seen.add(date)
        if not isinstance(r.get('title'), str) or not isinstance(r.get('items'), list) or not r['items']:
            raise ValueError('Incomplete report')
        for item in r['items']:
            for key in ('category', 'title', 'summary', 'insight', 'question', 'url'):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    raise ValueError('Missing item field: ' + key)
            if not item['url'].startswith('https://'):
                raise ValueError('Source must use HTTPS')


def generate(data):
    validate(data)  # Validate everything before touching files.
    out, events, platforms, topics = {}, {}, {}, {}
    latest = max(r['date'] for r in data)
    for report in sorted(data, key=lambda r: r['date']):
        refs = []
        for item in report['items']:
            eid = item.get('id') or 'E-' + hashlib.sha256((item['url'] + '\n' + item['title']).encode()).hexdigest()[:16]
            if not re.fullmatch(r'E-[A-Za-z0-9-]+', eid):
                raise ValueError('Invalid event id')
            if eid in events and events[eid]['title'] != item['title']:
                raise ValueError('Conflicting event identity')
            event = events.setdefault(eid, dict(item, issues=[]))
            # The newest issue supplies the current public summary.
            issues = event['issues']
            event.update(item)
            event['issues'] = issues + [report['date']]
            refs.append('[[' + eid + '|' + item['title'] + ']]')
        out['06-日报归档/D-' + report['date'] + '.md'] = md(report['title'], 'issue',
            '## 收录范围\n\n' + report.get('period', '') + '\n\n## 本期事件\n\n' + '\n'.join('- ' + x for x in refs)
            + '\n\n## 今日练习（假设）\n\n' + report.get('exercise', ''), issue_date=report['date'])
    for eid, event in events.items():
        text = ' '.join(event.get(k, '') for k in ('title', 'summary', 'insight'))
        ks = ['K-03-指标口径与因果']
        for keywords, key in [('利润 成本 退款', 'K-01-贡献利润'), ('履约 核销 订单 转化 到场', 'K-02-转化与履约'), ('商家 激励 补贴 工具', 'K-04-商家分层与激励'), ('主图 图片 素材 商品 质量', 'K-05-商品表达与信任')]:
            if any(x in text for x in keywords.split()):
                ks.append(key)
        topic = 'T-AI与经营' if any(x in text for x in ('AI', '智能', '自动化')) else 'T-交易与平台治理'
        topics.setdefault(topic, []).append(eid)
        ps = [p for p in ('抖音', '快手', '小红书', '美团', '京东', '天猫', '速卖通', 'Etsy', 'Google', 'TikTok', '亚马逊', '申通', '东方甄选') if p in text]
        for p in ps:
            platforms.setdefault(p, []).append(eid)
        source = 'S-' + eid[2:]
        verification = event.get('verification_status', '历史归档-本轮未复核')
        out['07-来源资料/' + source + '.md'] = md(event['title'] + '｜来源', 'source',
            '## 原文链接\n\n' + event['url'] + '\n\n## 核实状态\n\n' + verification
            + '\n\n迁入来源链接不等于重新核实。本卡没有录入逐字引语。\n\n## 支撑事件\n\n[[' + eid + ']]',
            url=event['url'], published_date=event.get('published_date'), verification_status=verification)
        out['01-动态事件/' + eid + '.md'] = md(event['title'], 'event',
            '## 报道事实摘要\n\n' + event['summary'] + '\n\n## 运营分析（推断）\n\n' + event['insight']
            + '\n\n## 来源\n\n[[' + source + ']]\n\n## 知识关联\n\n'
            + '\n'.join('- [[' + k + ']]：作为本事件的分析框架，不代表该事件已验证此规律。' for k in ks)
            + '\n\n## 专题与平台\n\n[[' + topic + ']] ' + ' '.join('[[P-' + p + ']]' for p in ps)
            + '\n\n## 面试思考\n\n' + event['question']
            + '\n\n## 收录记录\n\n' + '、'.join('[[D-' + d + ']]' for d in event['issues']),
            id=eid, category=event['category'], platforms=ps, event_date=event.get('event_date'),
            published_date=event.get('published_date'), first_seen=min(event['issues']), last_seen=max(event['issues']),
            verification_status=verification, sources=['[[' + source + ']]'])
    for key, body in KNOWLEDGE.items():
        out['03-通用知识/' + key + '.md'] = md(key[5:], 'knowledge', body + '\n\n## 边界\n\n此为分析框架草案，不是单篇新闻证明的实证结论。相关事件见反向链接。', status='框架草案')
    for topic, ids in topics.items():
        out['02-专题追踪/' + topic + '.md'] = md(topic[2:], 'topic', '\n'.join('- [[' + eid + '|' + events[eid]['title'] + ']]' for eid in ids))
    for platform, ids in platforms.items():
        out['04-平台与公司/P-' + platform + '.md'] = md(platform, 'platform',
            '平台模型、产品、地域、版本和指标口径分别核对，不用统一模型替代原生定义。\n\n'
            + '\n'.join('- [[' + eid + '|' + events[eid]['title'] + ']]' for eid in ids))
    out['00-首页与导航/首页.md'] = md('商业化日报 · 公开阅读库', 'index',
        '自动生成的公开日报阅读副本；个人笔记请保存在独立私有库。\n\n'
        + f'当前共 {len(data)} 期，{len(events)} 个事件；最新 {latest}。\n\n## 日报\n\n'
        + '\n'.join('- [[D-' + r['date'] + '|' + r['date'] + ']]' for r in sorted(data, key=lambda r: r['date'], reverse=True))
        + '\n\n## 专题\n\n' + '\n'.join('- [[' + x + ']]' for x in topics)
        + '\n\n## 知识\n\n' + '\n'.join('- [[' + x + ']]' for x in KNOWLEDGE))
    return out


def sync(base=BASE):
    data = json.loads((base / 'reports.json').read_text(encoding='utf-8'))
    files = generate(data)
    vault = base / 'vault'
    manifest = vault / '.generated-manifest.json'
    previous = json.loads(manifest.read_text()) if manifest.exists() else []
    # Only remove files previously declared generated, never user-created notes.
    for name in previous:
        target = (vault / name).resolve()
        if vault.resolve() not in target.parents:
            raise ValueError('Invalid generated path')
    for name in previous:
        if name not in files:
            (vault / name).unlink(missing_ok=True)
    for name, content in files.items():
        target = vault / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_text(encoding='utf-8') != content:
            target.write_text(content, encoding='utf-8')
    manifest.write_text(json.dumps(sorted(files), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Validated {len(data)} issues; generated {len(files)} public notes')


if __name__ == '__main__':
    sync()
