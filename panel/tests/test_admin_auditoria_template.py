from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_admin_sidebar_has_auditoria_link():
    template = ROOT.joinpath('templates', 'layouts', 'base_admin.html').read_text()

    assert 'href="#auditoria"' in template
    assert 'data-section="auditoria"' in template


def test_admin_dashboard_has_auditoria_panel():
    template = ROOT.joinpath('templates', 'panel', 'admin_dashboard.html').read_text()

    assert 'id="panel-auditoria"' in template
    assert 'auditorias_recientes' in template
    assert 'verificaciones_auditoria_recientes' in template
