#!/usr/bin/env python3
"""Render an arch-viz JSON block from Markdown into an interactive architecture HTML."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# HTML template — fully data-driven via CONFIG injection
# ---------------------------------------------------------------------------

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --surface2: #1c2433; --surface3: #21262d;
    --border: #30363d; --border2: #3d444d; --text: #e6edf3; --text2: #8b949e; --text3: #6e7681;
    --green: #3fb950; --green-dim: #1a4a1e; --red: #f85149; --red-dim: #4a1a1a;
    --blue: #58a6ff; --blue-dim: #1a2a4a; --purple: #bc8cff; --purple-dim: #2d1a4a;
    --orange: #ff9500; --orange-dim: #3a2a00; --yellow: #e3b341; --cyan: #39d353;
    --teal: #2dd4bf; --pink: #f778ba; --accent: #238636;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

  header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 0 24px; height: 56px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
  .header-brand { display: flex; align-items: center; gap: 12px; }
  .header-logo { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
  .header-title { font-size: 15px; font-weight: 600; }
  .header-sub { font-size: 12px; color: var(--text2); margin-top: 1px; }
  .header-tabs { display: flex; gap: 4px; }
  .tab-btn { background: none; border: none; color: var(--text2); padding: 6px 14px; border-radius: 6px; font-size: 13px; font-family: inherit; cursor: pointer; transition: all 0.15s; }
  .tab-btn:hover { background: var(--surface3); color: var(--text); }
  .tab-btn.active { background: var(--surface3); color: var(--text); font-weight: 500; }

  .main { display: flex; flex: 1; overflow: hidden; }

  /* Left sidebar */
  .sidebar { width: 260px; flex-shrink: 0; background: var(--surface); border-right: 1px solid var(--border); overflow-y: auto; padding: 16px 12px; }
  .sidebar-section-label { font-size: 10px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text3); padding: 0 8px; margin-bottom: 8px; margin-top: 4px; }
  .identity-card { border-radius: 8px; border: 1px solid var(--border); padding: 12px; cursor: pointer; transition: all 0.15s; margin-bottom: 6px; position: relative; overflow: hidden; }
  .identity-card:hover { border-color: var(--border2); background: var(--surface2); }
  .identity-card.active { border-color: var(--blue); background: var(--blue-dim); }
  .identity-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; border-radius: 2px 0 0 2px; }
  .identity-card.active::before { background: var(--blue); }
  .card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
  .card-avatar { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
  .card-name { font-size: 13px; font-weight: 600; }
  .card-auth { font-size: 10px; padding: 1px 6px; border-radius: 4px; font-weight: 500; font-family: 'JetBrains Mono', monospace; }
  .card-desc { font-size: 11px; color: var(--text2); line-height: 1.5; }
  .infra-section { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
  .infra-item { display: flex; justify-content: space-between; align-items: flex-start; padding: 6px 8px; border-radius: 5px; margin-bottom: 3px; }
  .infra-label { font-size: 10px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.05em; }
  .infra-val { font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--text2); text-align: right; max-width: 140px; word-break: break-all; }

  /* Right panel */
  .panel { flex: 1; overflow-y: auto; padding: 24px 28px; display: none; }
  .panel.active { display: block; }

  /* Identity view */
  .view-header { margin-bottom: 20px; }
  .view-title { font-size: 20px; font-weight: 700; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; }
  .view-badges { display: flex; gap: 6px; flex-wrap: wrap; }
  .badge { font-size: 11px; padding: 3px 8px; border-radius: 4px; font-weight: 500; font-family: 'JetBrains Mono', monospace; }

  /* Network path */
  .network-path { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px 24px; margin-bottom: 16px; }
  .network-path-title { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 16px; }
  .infra-flow { display: flex; align-items: center; gap: 0; }
  .infra-node { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; text-align: center; min-width: 100px; flex-shrink: 0; }
  .infra-node-icon { font-size: 20px; margin-bottom: 4px; }
  .infra-node-name { font-size: 12px; font-weight: 600; }
  .infra-node-sub { font-size: 10px; color: var(--text3); margin-top: 2px; }
  .infra-arrow { flex: 1; position: relative; height: 24px; display: flex; align-items: center; min-width: 40px; }
  .arrow-line { height: 2px; background: linear-gradient(90deg, var(--border), var(--blue-dim), var(--border)); width: 100%; position: relative; }
  .arrow-line::after { content: '›'; position: absolute; right: -4px; top: 50%; transform: translateY(-50%); color: var(--border2); font-size: 14px; }
  .animated-dot { width: 8px; height: 8px; background: var(--blue); border-radius: 50%; position: absolute; top: 50%; transform: translateY(-50%); animation: flowdot 2s ease-in-out infinite; box-shadow: 0 0 6px var(--blue); }
  @keyframes flowdot { 0% { left: 0; opacity: 1; } 80% { opacity: 1; } 100% { left: calc(100% - 8px); opacity: 0; } }

  /* Auth steps */
  .steps-section { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px 24px; margin-bottom: 16px; }
  .steps-title { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 16px; }
  .step-item { display: flex; gap: 14px; margin-bottom: 16px; opacity: 0; transform: translateY(8px); transition: all 0.3s ease; }
  .step-item.visible { opacity: 1; transform: translateY(0); }
  .step-num { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; }
  .step-body { flex: 1; }
  .step-node { font-size: 11px; font-weight: 600; margin-bottom: 2px; }
  .step-action { font-size: 13px; color: var(--text); margin-bottom: 4px; }
  .step-detail { font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--text2); background: var(--bg); padding: 5px 8px; border-radius: 5px; border: 1px solid var(--border); }

  /* Two-col layout */
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }

  /* Policy grid */
  .policy-section { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px 24px; }
  .policy-title { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px; }
  .policy-grid { display: flex; flex-direction: column; gap: 6px; }
  .policy-item { display: flex; align-items: center; gap: 8px; padding: 5px 8px; border-radius: 6px; font-size: 11px; font-family: 'JetBrains Mono', monospace; }
  .policy-item.allow { background: var(--green-dim); color: var(--green); }
  .policy-item.deny { background: var(--red-dim); color: var(--red); opacity: 0.7; }
  .policy-icon { font-size: 13px; flex-shrink: 0; }

  /* Audit log */
  .audit-section { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px 24px; }
  .audit-title { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px; }
  .audit-log { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px 14px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--green); line-height: 1.8; }
  .audit-log .dim { color: var(--text3); }
  .audit-log .key { color: var(--blue); }
  .audit-log .val { color: var(--yellow); }

  /* Alert box */
  .alert-box { border-radius: 8px; padding: 12px 14px; margin-top: 16px; border: 1px solid; font-size: 12px; line-height: 1.6; }
  .alert-box.blue { background: var(--blue-dim); border-color: var(--blue); }
  .alert-box.orange { background: var(--orange-dim); border-color: var(--orange); }
  .alert-box.green { background: var(--green-dim); border-color: var(--green); }
  .alert-icon { font-size: 14px; margin-right: 6px; }

  /* Flows tab */
  .flow-view { max-width: 760px; }
  .flow-header { margin-bottom: 24px; }
  .flow-title { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
  .flow-desc { font-size: 13px; color: var(--text2); margin-bottom: 12px; line-height: 1.6; }
  .flow-badges { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
  .flow-badge { font-size: 11px; padding: 3px 10px; border-radius: 12px; background: var(--surface2); border: 1px solid var(--border); color: var(--text2); }
  .flow-step { display: flex; gap: 0; margin-bottom: 0; }
  .flow-step-left { width: 120px; flex-shrink: 0; text-align: right; padding-right: 20px; padding-top: 4px; }
  .flow-actor { font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px; display: inline-block; }
  .flow-step-mid { width: 32px; flex-shrink: 0; display: flex; flex-direction: column; align-items: center; }
  .flow-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; border: 2px solid var(--bg); }
  .flow-line { width: 2px; flex: 1; background: var(--border); min-height: 30px; }
  .flow-step-right { flex: 1; padding-left: 16px; padding-bottom: 28px; }
  .flow-event { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
  .flow-detail { font-size: 12px; color: var(--text2); margin-bottom: 8px; line-height: 1.5; }
  .flow-code { font-family: 'JetBrains Mono', monospace; font-size: 11px; background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; padding: 10px 12px; color: var(--text2); white-space: pre; overflow-x: auto; }
  .flow-step-enter { opacity: 0; transform: translateX(12px); transition: all 0.35s ease; }
  .flow-step-enter.visible { opacity: 1; transform: translateX(0); }
  .state-map { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; margin-top: 8px; }
  .state-map-title { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; }
  .state-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); }
  .state-row:last-child { border-bottom: none; }
  .state-trigger { font-size: 12px; font-family: 'JetBrains Mono', monospace; color: var(--text2); }
  .state-result { font-size: 12px; font-weight: 600; }
  .multi-flow-nav { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px; }
  .flow-nav-btn { background: var(--surface); border: 1px solid var(--border); color: var(--text2); padding: 6px 14px; border-radius: 6px; font-size: 12px; font-family: inherit; cursor: pointer; transition: all 0.15s; }
  .flow-nav-btn:hover { background: var(--surface3); color: var(--text); }
  .flow-nav-btn.active { background: var(--surface3); border-color: var(--blue); color: var(--blue); }
  .flow-content { display: none; }
  .flow-content.active { display: block; }

  .empty-state { display: flex; align-items: center; justify-content: center; height: 300px; color: var(--text3); font-size: 14px; }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
</style>
</head>
<body>
<header>
  <div class="header-brand" id="header-brand"></div>
  <div class="header-tabs">
    <button class="tab-btn active" onclick="switchPanel('identities')">Identities</button>
    <button class="tab-btn" id="flows-tab-btn" onclick="switchPanel('flows')">Flows</button>
  </div>
</header>
<div class="main">
  <div class="sidebar" id="sidebar"></div>
  <div class="panel active" id="panel-identities"><div id="identity-view"></div></div>
  <div class="panel" id="panel-flows"><div class="flow-view" id="flows-view"></div></div>
</div>

<script>
const CONFIG = __CONFIG_PLACEHOLDER__;

let activeIdentity = null;
let activeFlow = 0;

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  renderHeader();
  renderSidebar();
  if (CONFIG.identities && CONFIG.identities.length > 0) {
    selectIdentity(CONFIG.identities[0].id);
  } else {
    document.getElementById('identity-view').innerHTML = '<div class="empty-state">No identities defined in config.</div>';
  }
  renderFlowsPanel();
  if (!CONFIG.flows || CONFIG.flows.length === 0) {
    document.getElementById('flows-tab-btn').style.display = 'none';
  }
});

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------
function renderHeader() {
  const proj = CONFIG.project || {};
  const grad = proj.logoGradient || 'linear-gradient(135deg, #238636, #2ea043)';
  const icon = proj.logoIcon || '🏗';
  document.getElementById('header-brand').innerHTML = `
    <div class="header-logo" style="background:${grad}">${icon}</div>
    <div>
      <div class="header-title">${esc(proj.title || 'Architecture')}</div>
      ${proj.subtitle ? `<div class="header-sub">${esc(proj.subtitle)}</div>` : ''}
    </div>
  `;
}

// ---------------------------------------------------------------------------
// Sidebar
// ---------------------------------------------------------------------------
function renderSidebar() {
  const sb = document.getElementById('sidebar');
  let html = '';
  if (CONFIG.identities && CONFIG.identities.length > 0) {
    html += `<div class="sidebar-section-label">Identities</div>`;
    for (const id of CONFIG.identities) {
      const grad = id.avatarGradient || 'linear-gradient(135deg, #238636, #2ea043)';
      const authColor = id.authColor || 'var(--text2)';
      const authBg = id.authBg || 'var(--surface3)';
      html += `
        <div class="identity-card" id="card-${esc(id.id)}" onclick="selectIdentity('${esc(id.id)}')">
          <div class="card-header">
            <div class="card-avatar" style="background:${grad}">${esc(id.icon || '?')}</div>
            <div>
              <div class="card-name">${esc(id.name)}</div>
              <span class="card-auth" style="background:${authBg};color:${authColor}">${esc(id.authType || '')}</span>
            </div>
          </div>
          <div class="card-desc">${esc(id.description || '')}</div>
        </div>`;
    }
  }
  if (CONFIG.infrastructure && CONFIG.infrastructure.length > 0) {
    html += `<div class="infra-section"><div class="sidebar-section-label">Infrastructure</div>`;
    for (const item of CONFIG.infrastructure) {
      html += `
        <div class="infra-item">
          <span class="infra-label">${esc(item.label)}</span>
          <span class="infra-val">${esc(item.value)}</span>
        </div>`;
    }
    html += '</div>';
  }
  sb.innerHTML = html;
}

// ---------------------------------------------------------------------------
// Identity view
// ---------------------------------------------------------------------------
function selectIdentity(id) {
  activeIdentity = id;
  document.querySelectorAll('.identity-card').forEach(c => c.classList.remove('active'));
  const card = document.getElementById('card-' + id);
  if (card) card.classList.add('active');
  const identity = CONFIG.identities.find(i => i.id === id);
  if (!identity) return;
  renderIdentityView(identity);
}

function renderIdentityView(id) {
  const view = document.getElementById('identity-view');
  // Badges
  const badges = (id.badges || []).map(b =>
    `<span class="badge" style="background:${b.bg||'var(--surface3)'};color:${b.color||'var(--text2)'}">${esc(b.text)}</span>`
  ).join('');

  // Network path
  const nodes = id.networkPath || [];
  let networkHtml = '';
  nodes.forEach((n, i) => {
    networkHtml += `<div class="infra-node"><div class="infra-node-icon">${esc(n.icon||'?')}</div><div class="infra-node-name">${esc(n.name)}</div><div class="infra-node-sub">${esc(n.subtext||'')}</div></div>`;
    if (i < nodes.length - 1) {
      networkHtml += `<div class="infra-arrow"><div class="arrow-line"><div class="animated-dot" style="animation-delay:${i*0.5}s"></div></div></div>`;
    }
  });

  // Steps
  const steps = id.steps || [];
  const stepHtml = steps.map((s, i) => `
    <div class="step-item" id="step-${id.id}-${i}">
      <div class="step-num" style="background:${s.numberBg||'var(--surface3)'};color:${s.nodeColor||'var(--text)'}">${i+1}</div>
      <div class="step-body">
        <div class="step-node" style="color:${s.nodeColor||'var(--text)'}">${esc(s.node)}</div>
        <div class="step-action">${esc(s.action)}</div>
        <div class="step-detail">${esc(s.detail)}</div>
      </div>
    </div>`).join('');

  // Policies
  const allows = (id.policies && id.policies.allow || []).map(p =>
    `<div class="policy-item allow"><span class="policy-icon">✓</span>secret/data/${esc(p)}</div>`).join('');
  const denies = (id.policies && id.policies.deny || []).map(p =>
    `<div class="policy-item deny"><span class="policy-icon">✗</span>${esc(p)}</div>`).join('');

  // Audit log
  const auditLines = (id.auditLog || '').split('\n').map(line => {
    return line.replace(/([a-z_]+)=([^\s|]+)/g, (_, k, v) =>
      `<span class="key">${k}</span>=<span class="val">${v}</span>`);
  }).join('\n');

  // Alert
  const alert = id.alert;
  const alertHtml = alert ? `
    <div class="alert-box ${esc(alert.type||'blue')}">
      <span class="alert-icon">${esc(alert.icon||'ℹ️')}</span>${esc(alert.text||'')}
    </div>` : '';

  view.innerHTML = `
    <div class="view-header">
      <div class="view-title">${esc(id.icon||'')} ${esc(id.name)}</div>
      <div class="view-badges">${badges}</div>
    </div>
    ${nodes.length > 0 ? `
    <div class="network-path">
      <div class="network-path-title">Network Path</div>
      <div class="infra-flow">${networkHtml}</div>
    </div>` : ''}
    <div class="steps-section">
      <div class="steps-title">Auth Flow</div>
      ${stepHtml}
    </div>
    <div class="two-col">
      <div class="policy-section">
        <div class="policy-title">Policy Scope</div>
        <div class="policy-grid">${allows}${denies}</div>
      </div>
      <div class="audit-section">
        <div class="audit-title">Audit Log Entry</div>
        <div class="audit-log">${auditLines}</div>
      </div>
    </div>
    ${alertHtml}
  `;

  // Stagger step animations
  steps.forEach((_, i) => {
    setTimeout(() => {
      const el = document.getElementById(`step-${id.id}-${i}`);
      if (el) el.classList.add('visible');
    }, i * 80);
  });
}

// ---------------------------------------------------------------------------
// Flows panel
// ---------------------------------------------------------------------------
function renderFlowsPanel() {
  const flows = CONFIG.flows || [];
  if (flows.length === 0) return;
  const view = document.getElementById('flows-view');

  let navHtml = '';
  let contentHtml = '';

  flows.forEach((flow, fi) => {
    const isActive = fi === 0;
    navHtml += `<button class="flow-nav-btn ${isActive ? 'active' : ''}" onclick="selectFlow(${fi})" id="flownav-${fi}">${esc(flow.title)}</button>`;

    const badges = (flow.badges || []).map(b => `<span class="flow-badge">${esc(b)}</span>`).join('');
    const steps = flow.steps || [];
    const stepHtml = steps.map((s, i) => `
      <div class="flow-step flow-step-enter" id="fstep-${fi}-${i}">
        <div class="flow-step-left">
          <span class="flow-actor" style="background:${s.actorBg||'var(--surface3)'};color:${s.actorColor||'var(--text)'}">${esc(s.actor)}</span>
        </div>
        <div class="flow-step-mid">
          <div class="flow-dot" style="background:${s.dotColor||'var(--blue)'}"></div>
          ${i < steps.length - 1 ? '<div class="flow-line"></div>' : ''}
        </div>
        <div class="flow-step-right">
          <div class="flow-event">${esc(s.event)}</div>
          <div class="flow-detail">${esc(s.detail)}</div>
          ${s.code ? `<div class="flow-code">${esc(s.code)}</div>` : ''}
        </div>
      </div>`).join('');

    const stateMappings = flow.stateMappings || [];
    const stateHtml = stateMappings.length > 0 ? `
      <div class="state-map">
        <div class="state-map-title">State Mapping</div>
        ${stateMappings.map(m => `
          <div class="state-row">
            <span class="state-trigger">${esc(m.trigger)}</span>
            <span class="state-result" style="color:${m.resultColor||'var(--text)'}">${esc(m.result)}</span>
          </div>`).join('')}
      </div>` : '';

    contentHtml += `
      <div class="flow-content ${isActive ? 'active' : ''}" id="flow-content-${fi}">
        <div class="flow-header">
          <div class="flow-title">${esc(flow.title)}</div>
          <div class="flow-desc">${esc(flow.description || '')}</div>
          <div class="flow-badges">${badges}</div>
        </div>
        ${stepHtml}
        ${stateHtml}
      </div>`;
  });

  view.innerHTML = `<div class="multi-flow-nav">${navHtml}</div>${contentHtml}`;
  if (flows.length > 0) animateFlowSteps(0);
}

function selectFlow(fi) {
  activeFlow = fi;
  document.querySelectorAll('.flow-nav-btn').forEach((b, i) => b.classList.toggle('active', i === fi));
  document.querySelectorAll('.flow-content').forEach((c, i) => c.classList.toggle('active', i === fi));
  animateFlowSteps(fi);
}

function animateFlowSteps(fi) {
  const flow = CONFIG.flows && CONFIG.flows[fi];
  if (!flow) return;
  (flow.steps || []).forEach((_, i) => {
    setTimeout(() => {
      const el = document.getElementById(`fstep-${fi}-${i}`);
      if (el) el.classList.add('visible');
    }, i * 100);
  });
}

// ---------------------------------------------------------------------------
// Panel switcher
// ---------------------------------------------------------------------------
function switchPanel(name) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  event.target.classList.add('active');
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------
function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(value: str, max_len: int = 80) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    return (slug or "arch-viz")[:max_len]


def first_h1(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def extract_arch_viz_block(markdown: str) -> dict:
    pattern = re.compile(
        r"```(?:arch-viz|arch_viz)\s*\n(.*?)```",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        raise ValueError(
            "No ```arch-viz fenced block found in the Markdown file.\n"
            "Add a block like:\n\n```arch-viz\n{ ... JSON config ... }\n```"
        )
    raw = match.group(1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in arch-viz block: {exc}") from exc


def build_html(config: dict, title: str) -> str:
    config_json = json.dumps(config, ensure_ascii=False)
    html = TEMPLATE.replace("__TITLE__", title).replace("__CONFIG_PLACEHOLDER__", config_json)
    return html


def run_static_checks(output: Path, title: str) -> None:
    errors = []
    if not output.is_file():
        errors.append(f"output file missing: {output}")
    elif output.stat().st_size < 1000:
        errors.append(f"output file suspiciously small ({output.stat().st_size} bytes): {output}")
    else:
        content = output.read_text(encoding="utf-8")
        if title not in content:
            errors.append(f"title '{title}' not found in generated HTML")
        if "CONFIG" not in content:
            errors.append("CONFIG placeholder was not substituted")
    if errors:
        raise RuntimeError("static checks failed:\n" + "\n".join(f"  - {e}" for e in errors))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render an arch-viz JSON block from Markdown into interactive HTML."
    )
    parser.add_argument("input", type=Path, help="Markdown file containing an arch-viz fenced block.")
    parser.add_argument("--output", type=Path, help="Output HTML path. Defaults to ~/Desktop/<slug>-arch-viz.html.")
    parser.add_argument("--title", help="Override the page title.")
    parser.add_argument("--no-open", action="store_true", help="Do not open the generated HTML.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source = args.input.expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError(f"Input file not found: {source}")
        if source.suffix.lower() != ".md":
            raise ValueError(f"Expected a .md file, got: {source}")

        markdown = source.read_text(encoding="utf-8")
        config = extract_arch_viz_block(markdown)

        project = config.get("project", {})
        title = args.title or project.get("title") or first_h1(markdown) or source.stem.replace("-", " ").title()

        if args.output:
            output = args.output.expanduser().resolve()
        else:
            slug = slugify(title)
            output = Path.home() / "Desktop" / f"{slug}-arch-viz.html"

        output.parent.mkdir(parents=True, exist_ok=True)
        html = build_html(config, title)
        output.write_text(html, encoding="utf-8")

        run_static_checks(output, title)

        print(f"html={output}")

        if not args.no_open:
            subprocess.run(["open", str(output)], check=True)

        return 0

    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
