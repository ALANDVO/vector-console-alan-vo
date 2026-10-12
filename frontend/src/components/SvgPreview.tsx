import React, { useState } from 'react';

interface SvgPreviewProps {
  svgContent: string;
  title: string;
  htmlContent?: string;
}

export const SvgPreview: React.FC<SvgPreviewProps> = ({ svgContent, title, htmlContent }) => {
  const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');

  const downloadSvg = () => {
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, '-')}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadHtml = () => {
    if (!htmlContent) return;
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, '-')}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <div>
          <h2 className="card-title">Editorial Vector Canvas</h2>
          <p className="card-desc" style={{ marginBottom: 0 }}>Crisp SVG geometry · Zero drop shadows · Monospace metrics</p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className={`btn btn-sm ${viewMode === 'preview' ? 'btn-primary' : ''}`}
            onClick={() => setViewMode('preview')}
          >
            Render
          </button>
          <button
            className={`btn btn-sm ${viewMode === 'code' ? 'btn-primary' : ''}`}
            onClick={() => setViewMode('code')}
          >
            SVG Code
          </button>
          <button className="btn btn-sm" onClick={downloadSvg} title="Export pure SVG">
            Export SVG
          </button>
          {htmlContent && (
            <button className="btn btn-sm" onClick={downloadHtml} title="Export self-contained HTML">
              Export HTML
            </button>
          )}
        </div>
      </div>

      <div style={{ flex: 1, minHeight: '440px', background: '#ffffff', border: '1px solid var(--border-color)', borderRadius: '4px', overflow: 'auto', padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {viewMode === 'preview' ? (
          <div
            style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center' }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        ) : (
          <pre
            className="mono"
            style={{
              width: '100%',
              height: '100%',
              fontSize: '0.75rem',
              color: '#334155',
              overflow: 'auto',
              whiteSpace: 'pre-wrap'
            }}
          >
            {svgContent}
          </pre>
        )}
      </div>
    </div>
  );
};
