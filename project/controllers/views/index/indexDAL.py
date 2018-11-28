from controllers.models.models import AssetmanageAsset, VulnmanageScanvuln, LoopholeVuln, db


def index_info():
    db.session.commit()  # 清楚程序以及数据库层面带来的缓存问题
    info_dict = {}
    vuln_cnvd_count = len(LoopholeVuln.query.all())
    vuln_scan_count = len(VulnmanageScanvuln.query.all())
    vuln_scan_solve_count = len(VulnmanageScanvuln.query.filter(VulnmanageScanvuln.Leave != 0).all())
    asset_count = len(AssetmanageAsset.query.all())
    info_dict['vuln_cnvd_count'] = vuln_cnvd_count
    info_dict['vuln_scan_count'] = vuln_scan_count
    info_dict['vuln_scan_solve_count'] = vuln_scan_solve_count
    info_dict['asset_count'] = asset_count
    return info_dict
