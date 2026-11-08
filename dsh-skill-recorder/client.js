window.__ModuleLoader__.load({
  id: 'dsh-skill-recorder',
  factory: (require) => {
    const React = require('react');
    const h = React.createElement;
    const { useEffect, useRef, useState } = React;

    const ROUTE = 'api/skill-recorder';

    async function call(endpoint, payload) {
      const res = await fetch(ROUTE, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ endpoint, payload: payload || null }),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return await res.json();
    }

    function fmt(ms) {
      const total = Math.max(0, Math.floor(ms / 1000));
      const m = String(Math.floor(total / 60)).padStart(2, '0');
      const s = String(total % 60).padStart(2, '0');
      return m + ':' + s;
    }

    function when(iso) {
      if (!iso) return '';
      const d = new Date(iso);
      const pad = (n) => String(n).padStart(2, '0');
      return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    }

    function RecorderButton() {
      const [rec, setRec] = useState(null);
      const [ready, setReady] = useState(false);
      const [busy, setBusy] = useState(false);
      const [note, setNote] = useState(null);
      const [, tick] = useState(0);
      const mounted = useRef(true);

      async function refresh() {
        try {
          const r = await call('status');
          if (!mounted.current) return;
          setRec(r.recording || null);
          setReady(true);
          if (r.last && r.last.ok === false && r.last.error) setNote({ kind: 'error', text: String(r.last.error) });
        } catch (e) {
          if (mounted.current) setReady(false);
        }
      }

      useEffect(() => {
        mounted.current = true;
        refresh();
        const id = setInterval(refresh, 2000);
        const t = setInterval(() => tick((n) => n + 1), 1000);
        return () => {
          mounted.current = false;
          clearInterval(id);
          clearInterval(t);
        };
      }, []);

      useEffect(() => {
        if (!note) return;
        const id = setTimeout(() => setNote(null), 8000);
        return () => clearTimeout(id);
      }, [note]);

      async function onClick() {
        if (busy) return;
        setBusy(true);
        setNote(null);
        try {
          if (rec) {
            const r = await call('stop');
            setRec(null);
            const c = r && r.compile;
            if (r && r.ok && c) {
              setNote({ kind: 'ok', text: `已生成草案：${c.steps} 步，${c.needsReview} 步待确认` });
            } else if (r && r.ok && r.warning) {
              setNote({ kind: 'warn', text: r.warning });
            } else {
              setNote({ kind: 'error', text: (r && r.error) || '停止或编译失败' });
            }
          } else {
            const r = await call('start', {});
            if (r && r.ok && r.recording) {
              setRec(r.recording);
              setNote({ kind: 'ok', text: '开始录制，去操作手机吧' });
            } else {
              setNote({ kind: 'error', text: (r && (r.error || (r.last && r.last.error))) || '无法开始录制' });
            }
          }
        } catch (e) {
          setNote({ kind: 'error', text: String(e && e.message ? e.message : e) });
        } finally {
          setBusy(false);
          refresh();
        }
      }

      const elapsed = rec && rec.startedAt ? fmt(Date.now() - new Date(rec.startedAt).getTime()) : null;
      const dotColor = busy ? '#9ca3af' : rec ? '#ef4444' : '#10b981';

      const buttonStyle = {
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        height: 28,
        padding: '0 10px',
        borderRadius: 999,
        border: '1px solid ' + (rec ? 'rgba(239,68,68,.45)' : 'var(--dsw-alias-border-l2,#e5e7eb)'),
        background: rec ? 'rgba(239,68,68,.08)' : 'transparent',
        color: 'var(--dsw-alias-label-secondary,inherit)',
        font: 'inherit',
        fontSize: 12,
        lineHeight: '1',
        cursor: busy ? 'progress' : 'pointer',
        whiteSpace: 'nowrap',
        flex: 'none',
      };

      return h(
        'div',
        { style: { display: 'inline-flex', alignItems: 'center', gap: 8, minWidth: 0 } },
        h(
          'button',
          {
            type: 'button',
            onClick,
            disabled: busy || !ready,
            title: rec ? '停止录制并生成草案' : '录一遍手机操作，生成可回放的技能草案',
            style: buttonStyle,
          },
          h('span', {
            style: {
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: dotColor,
              boxShadow: rec ? '0 0 0 3px rgba(239,68,68,.14)' : 'none',
              animation: rec ? 'dshRecPulse 1.6s ease-in-out infinite' : 'none',
            },
          }),
          h('span', null, busy ? '处理中…' : rec ? '停止 ' + elapsed : '录制')
        ),
        note
          ? h(
              'span',
              {
                style: {
                  fontSize: 11,
                  lineHeight: '16px',
                  maxWidth: 240,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  color:
                    note.kind === 'error'
                      ? 'var(--dsw-alias-state-error-primary,#dc2626)'
                      : note.kind === 'warn'
                        ? 'var(--dsw-alias-state-warn-label,#c2410c)'
                        : 'var(--dsw-alias-label-tertiary,#6b7280)',
                },
                title: note.text,
              },
              note.text
            )
          : null,
        h('style', null, '@keyframes dshRecPulse{0%,100%{opacity:1}50%{opacity:.35}}')
      );
    }

    /* --------------------------- 录制库（精简版） --------------------------- */
    /* 只做三件事：选一份、生成文稿、发布成技能。列表只显示名字和时间。 */

    function LibraryButton() {
      const [open, setOpen] = useState(false);
      const [sessions, setSessions] = useState([]);
      const [sel, setSel] = useState(null);
      const [busy, setBusy] = useState(false);
      const [hint, setHint] = useState(null); // 一行提示，不占地方
      const [naming, setNaming] = useState(null);
      const [confirmClear, setConfirmClear] = useState(false);
      const anchorRef = useRef(null);
      const [pos, setPos] = useState(null);

      // 面板跟着「录制库」按钮走：算按钮在屏幕上的位置，把面板摆到它正上方
      useEffect(() => {
        if (!open) return undefined;
        const place = () => {
          const el = anchorRef.current;
          if (!el) return;
          const r = el.getBoundingClientRect();
          const width = Math.min(300, window.innerWidth - 20);
          const left = Math.min(Math.max(8, r.left), Math.max(8, window.innerWidth - width - 8));
          setPos({ left, bottom: Math.max(8, window.innerHeight - r.top + 8), width });
        };
        place();
        window.addEventListener('resize', place);
        return () => window.removeEventListener('resize', place);
      }, [open]);

      async function reload() {
        const r = await call('list');
        if (r && r.ok) setSessions(r.sessions || []);
      }

      useEffect(() => {
        reload().catch(() => {});
      }, []);

      async function toggle() {
        if (open) {
          setOpen(false);
          return;
        }
        setOpen(true);
        setHint(null);
        setConfirmClear(false);
        try {
          await reload();
        } catch (e) {
          setHint('读取失败');
        }
      }

      async function generate() {
        if (!sel) return;
        setBusy(true);
        setHint(null);
        try {
          const r = await call('compile-session', { id: sel });
          if (!r.ok) throw new Error(r.error || '生成失败');
          const n = (r.session && r.session.steps) || 0;
          setHint(`已生成 ${n} 步`);
          await reload();
        } catch (e) {
          setHint(String((e && e.message) || e));
        } finally {
          setBusy(false);
        }
      }

      async function publish() {
        if (!sel || !naming) return;
        setBusy(true);
        try {
          const r = await call('save-skill', { id: sel, skillName: naming, title: naming });
          if (!r.ok) throw new Error(r.error || '发布失败');
          setHint(`已存为技能 ${naming}`);
          setNaming(null);
        } catch (e) {
          setHint(String((e && e.message) || e));
        } finally {
          setBusy(false);
        }
      }

      async function clearAll() {
        setBusy(true);
        try {
          const r = await call('clear', {});
          if (!r.ok) throw new Error(r.error || '清空失败');
          setSel(null);
          setConfirmClear(false);
          await reload();
          setHint(`已清空 ${r.removed.length} 份`);
        } catch (e) {
          setHint(String((e && e.message) || e));
        } finally {
          setBusy(false);
        }
      }

      const btn = {
        height: 26,
        padding: '0 9px',
        borderRadius: 8,
        border: '1px solid var(--dsw-alias-border-l2,#e5e7eb)',
        background: 'transparent',
        color: 'var(--dsw-alias-label-secondary,inherit)',
        font: 'inherit',
        fontSize: 11.5,
        lineHeight: '1',
        cursor: 'pointer',
        whiteSpace: 'nowrap',
      };
      const danger = { ...btn, color: '#dc2626', borderColor: 'rgba(220,38,38,.35)' };

      const panel = open
        ? h(
            'div',
            {
              style: {
                position: 'fixed',
                left: pos ? pos.left : 8,
                bottom: pos ? pos.bottom : 60,
                width: pos ? pos.width : 300,
                maxHeight: '38vh',
                zIndex: 9999,
                visibility: pos ? 'visible' : 'hidden',
                display: 'flex',
                flexDirection: 'column',
                background: 'var(--dsw-alias-bg-layer-2,#fff)',
                border: '1px solid var(--dsw-alias-border-l2,#e5e7eb)',
                borderRadius: 12,
                boxShadow: '0 10px 28px rgba(0,0,0,.24)',
                overflow: 'hidden',
                fontSize: 12,
              },
            },
            h(
              'div',
              {
                style: {
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '7px 10px',
                  borderBottom: '1px solid var(--dsw-alias-border-l2,#eee)',
                },
              },
              h('b', { style: { fontSize: 12.5 } }, '录制库'),
              h('span', { style: { fontSize: 11, opacity: 0.55 } }, sessions.length ? `${sessions.length} 份` : ''),
              h('span', { style: { flex: 1 } }),
              h('button', { type: 'button', style: { ...btn, height: 22, padding: '0 7px' }, onClick: toggle }, '关闭')
            ),
            h(
              'div',
              { style: { overflow: 'auto', maxHeight: '24vh' } },
              sessions.length === 0
                ? h('div', { style: { padding: '12px 10px', opacity: 0.6 } }, '还没有录制')
                : sessions.map((s) =>
                    h(
                      'div',
                      {
                        key: s.id,
                        onClick: () => {
                          setSel(s.id);
                          setHint(null);
                        },
                        style: {
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6,
                          padding: '7px 10px',
                          cursor: 'pointer',
                          background: sel === s.id ? 'rgba(59,130,246,.12)' : 'transparent',
                          borderBottom: '1px solid var(--dsw-alias-border-l2,#f5f5f5)',
                        },
                      },
                      h('span', {
                        style: {
                          width: 6,
                          height: 6,
                          borderRadius: '50%',
                          flex: 'none',
                          background: s.hasStoryboard ? '#22c55e' : '#d1d5db',
                        },
                      }),
                      h(
                        'span',
                        {
                          style: {
                            flex: 1,
                            minWidth: 0,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          },
                        },
                        s.name
                      ),
                      h('span', { style: { fontSize: 10.5, opacity: 0.5, whiteSpace: 'nowrap' } }, when(s.startedAt))
                    )
                  )
            ),
            h(
              'div',
              {
                style: {
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '7px 10px',
                  borderTop: '1px solid var(--dsw-alias-border-l2,#eee)',
                },
              },
              naming
                ? [
                    h('input', {
                      key: 'n',
                      autoFocus: true,
                      value: naming,
                      onChange: (e) => setNaming(e.target.value),
                      placeholder: '技能名',
                      style: {
                        flex: 1,
                        minWidth: 0,
                        height: 24,
                        fontSize: 11.5,
                        padding: '0 6px',
                        borderRadius: 6,
                        border: '1px solid var(--dsw-alias-border-l2,#ddd)',
                      },
                    }),
                    h('button', { key: 's', type: 'button', style: btn, onClick: publish, disabled: busy || !naming.trim() }, '保存'),
                    h('button', { key: 'c', type: 'button', style: btn, onClick: () => setNaming(null) }, '取消')
                  ]
                : [
                    h('button', { key: 'g', type: 'button', style: btn, onClick: generate, disabled: busy || !sel }, '生成文稿'),
                    h('button', {
                      key: 'p',
                      type: 'button',
                      style: btn,
                      disabled: busy || !sel,
                      onClick: () =>
                        setNaming(String((sessions.find((x) => x.id === sel) || {}).name || 'my-skill').replace(/\s+/g, '-')),
                    }, '发布'),
                    h('span', { key: 'f', style: { flex: 1 } }),
                    confirmClear
                      ? [
                          h('button', { key: 'y', type: 'button', style: danger, onClick: clearAll, disabled: busy }, '确认清空'),
                          h('button', { key: 'n2', type: 'button', style: btn, onClick: () => setConfirmClear(false) }, '取消')
                        ]
                      : h('button', {
                          key: 'x',
                          type: 'button',
                          style: danger,
                          onClick: () => setConfirmClear(true),
                          disabled: busy || !sessions.length,
                        }, '清空')
                  ]
            ),
            hint ? h('div', { style: { padding: '5px 10px', fontSize: 11, opacity: 0.7, borderTop: '1px solid var(--dsw-alias-border-l2,#eee)' } }, hint) : null
          )
        : null;

      return h(
        'span',
        { ref: anchorRef, style: { display: 'inline-flex', alignItems: 'center', flex: 'none' } },
        h(
          'button',
          {
            type: 'button',
            onClick: toggle,
            style: {
              height: 28,
              padding: '0 10px',
              borderRadius: 999,
              border: '1px solid var(--dsw-alias-border-l2,#e5e7eb)',
              background: open ? 'rgba(59,130,246,.10)' : 'transparent',
              color: 'var(--dsw-alias-label-secondary,inherit)',
              font: 'inherit',
              fontSize: 12,
              lineHeight: '1',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              flex: 'none',
            },
            title: '选择以前录过的操作',
          },
          sessions.length ? `录制库 ${sessions.length}` : '录制库'
        ),
        panel
      );
    }


    function ComposerTools() {
      return h(
        'div',
        { style: { display: 'inline-flex', alignItems: 'center', gap: 8, minWidth: 0 } },
        h(RecorderButton, null),
        h(LibraryButton, null)
      );
    }

    return {
      inject: ['slots'],
      apply(ctx) {
        ctx.slots.inject('conversation.input.left', () =>
          ctx.slots.register(
            { name: 'conversation.input.left', id: 'skill-recorder', order: 5 },
            ComposerTools
          )
        );
      },
    };
  },
});
