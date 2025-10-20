# 模块文件名：param_check_store.py
from hull_interface import HullBasicParams, ParamCheckResult

# 全局变量：存储合格的参数（供其他模块读取，避免重复传递）
global_valid_params: Optional[HullBasicParams] = None


def check_hull_params(raw_params: HullBasicParams) -> ParamCheckResult:
    """
    功能：校验参数合理性（核心逻辑，基于船舶设计基本规则）
    输入：raw_params（子模块1传递的未校验参数）
    输出：ParamCheckResult对象（校验结果）
    校验规则（简化版，易实现）：
    1. Lpp > B（船长>船宽）
    2. B > T（船宽>吃水）
    3. D > T（型深>吃水）
    4. Delta > 0（排水量为正）
    5. 若输入Loa，需满足Loa ≥ Lpp（总长≥垂线间长）
    """
    error_msg = ""
    if raw_params.Lpp <= raw_params.B:
        error_msg = "错误：垂线间长（Lpp）必须大于船宽（B）"
    elif raw_params.B <= raw_params.T:
        error_msg = "错误：船宽（B）必须大于吃水（T）"
    elif raw_params.D <= raw_params.T:
        error_msg = "错误：型深（D）必须大于吃水（T）"
    elif raw_params.Delta <= 0:
        error_msg = "错误：排水量（Delta）必须大于0"
    elif raw_params.Loa is not None and raw_params.Loa < raw_params.Lpp:
        error_msg = "错误：总长（Loa）不能小于垂线间长（Lpp）"

    if not error_msg:
        return ParamCheckResult(
            is_valid=True,
            error_msg="",
            valid_params=raw_params
        )
    else:
        return ParamCheckResult(
            is_valid=False,
            error_msg=error_msg,
            valid_params=None
        )


def save_valid_params(params: HullBasicParams) -> None:
    """
    功能：存储合格的参数（供子模块3、5读取）
    输入：params（校验合格的HullBasicParams对象）
    输出：无（更新全局变量global_valid_params）
    """
    global global_valid_params
    global_valid_params = params


def get_valid_params() -> Optional[HullBasicParams]:
    """
    功能：提供合格参数给其他模块（子模块3、5调用）
    输入：无
    输出：global_valid_params（合格参数，若未存储则为None）
    """
    return global_valid_params