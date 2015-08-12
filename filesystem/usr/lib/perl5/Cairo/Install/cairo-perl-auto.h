/*
 * This file was automatically generated.  Do not edit.
 */

#include <cairo.h>

/* objects */

typedef cairo_t cairo_t_noinc;
typedef cairo_t cairo_t_ornull;
#define SvCairo(sv)			((cairo_t *) cairo_object_from_sv (sv, "Cairo::Context"))
#define SvCairo_ornull(sv)		(((sv) && SvOK (sv)) ? SvCairo(sv) : NULL)
#define newSVCairo(object)		(cairo_object_to_sv ((cairo_t *) cairo_reference (object), "Cairo::Context"))
#define newSVCairo_noinc(object)	(cairo_object_to_sv ((cairo_t *) object, "Cairo::Context"))
#define newSVCairo_ornull(object)	(((object) == NULL) ? &PL_sv_undef : newSVCairo(object))
typedef cairo_surface_t cairo_surface_t_noinc;
typedef cairo_surface_t cairo_surface_t_ornull;
#define SvCairoSurface(sv)			((cairo_surface_t *) cairo_object_from_sv (sv, "Cairo::Surface"))
#define SvCairoSurface_ornull(sv)		(((sv) && SvOK (sv)) ? SvCairoSurface(sv) : NULL)
#define newSVCairoSurface(object)		(cairo_object_to_sv ((cairo_surface_t *) cairo_surface_reference (object), "Cairo::Surface"))
#define newSVCairoSurface_noinc(object)	(cairo_object_to_sv ((cairo_surface_t *) object, "Cairo::Surface"))
#define newSVCairoSurface_ornull(object)	(((object) == NULL) ? &PL_sv_undef : newSVCairoSurface(object))
typedef cairo_font_face_t cairo_font_face_t_noinc;
typedef cairo_font_face_t cairo_font_face_t_ornull;
#define SvCairoFontFace(sv)			((cairo_font_face_t *) cairo_object_from_sv (sv, "Cairo::FontFace"))
#define SvCairoFontFace_ornull(sv)		(((sv) && SvOK (sv)) ? SvCairoFontFace(sv) : NULL)
#define newSVCairoFontFace(object)		(cairo_object_to_sv ((cairo_font_face_t *) cairo_font_face_reference (object), "Cairo::FontFace"))
#define newSVCairoFontFace_noinc(object)	(cairo_object_to_sv ((cairo_font_face_t *) object, "Cairo::FontFace"))
#define newSVCairoFontFace_ornull(object)	(((object) == NULL) ? &PL_sv_undef : newSVCairoFontFace(object))
typedef cairo_pattern_t cairo_pattern_t_noinc;
typedef cairo_pattern_t cairo_pattern_t_ornull;
#define SvCairoPattern(sv)			((cairo_pattern_t *) cairo_object_from_sv (sv, "Cairo::Pattern"))
#define SvCairoPattern_ornull(sv)		(((sv) && SvOK (sv)) ? SvCairoPattern(sv) : NULL)
#define newSVCairoPattern(object)		(cairo_object_to_sv ((cairo_pattern_t *) cairo_pattern_reference (object), "Cairo::Pattern"))
#define newSVCairoPattern_noinc(object)	(cairo_object_to_sv ((cairo_pattern_t *) object, "Cairo::Pattern"))
#define newSVCairoPattern_ornull(object)	(((object) == NULL) ? &PL_sv_undef : newSVCairoPattern(object))
typedef cairo_scaled_font_t cairo_scaled_font_t_noinc;
typedef cairo_scaled_font_t cairo_scaled_font_t_ornull;
#define SvCairoScaledFont(sv)			((cairo_scaled_font_t *) cairo_object_from_sv (sv, "Cairo::ScaledFont"))
#define SvCairoScaledFont_ornull(sv)		(((sv) && SvOK (sv)) ? SvCairoScaledFont(sv) : NULL)
#define newSVCairoScaledFont(object)		(cairo_object_to_sv ((cairo_scaled_font_t *) cairo_scaled_font_reference (object), "Cairo::ScaledFont"))
#define newSVCairoScaledFont_noinc(object)	(cairo_object_to_sv ((cairo_scaled_font_t *) object, "Cairo::ScaledFont"))
#define newSVCairoScaledFont_ornull(object)	(((object) == NULL) ? &PL_sv_undef : newSVCairoScaledFont(object))

/* structs */

typedef cairo_font_options_t cairo_font_options_t_ornull;
#define SvCairoFontOptions(sv)			((cairo_font_options_t *) cairo_struct_from_sv (sv, "Cairo::FontOptions"))
#define SvCairoFontOptions_ornull(sv)		(((sv) && SvOK (sv)) ? SvCairoFontOptions(sv) : NULL)
#define newSVCairoFontOptions(struct)		(cairo_struct_to_sv ((cairo_font_options_t *) struct, "Cairo::FontOptions"))
#define newSVCairoFontOptions_ornull(struct)	(((struct) == NULL) ? &PL_sv_undef : newSVCairoFontOptions(struct))
typedef cairo_matrix_t cairo_matrix_t_ornull;
#define SvCairoMatrix(sv)			((cairo_matrix_t *) cairo_struct_from_sv (sv, "Cairo::Matrix"))
#define SvCairoMatrix_ornull(sv)		(((sv) && SvOK (sv)) ? SvCairoMatrix(sv) : NULL)
#define newSVCairoMatrix(struct)		(cairo_struct_to_sv ((cairo_matrix_t *) struct, "Cairo::Matrix"))
#define newSVCairoMatrix_ornull(struct)	(((struct) == NULL) ? &PL_sv_undef : newSVCairoMatrix(struct))

/* enums */

int cairo_content_from_sv (SV * content);
SV * cairo_content_to_sv (int val);
#define SvCairoContent(sv)		(cairo_content_from_sv (sv))
#define newSVCairoContent(val)	(cairo_content_to_sv (val))
int cairo_line_cap_from_sv (SV * line_cap);
SV * cairo_line_cap_to_sv (int val);
#define SvCairoLineCap(sv)		(cairo_line_cap_from_sv (sv))
#define newSVCairoLineCap(val)	(cairo_line_cap_to_sv (val))
int cairo_antialias_from_sv (SV * antialias);
SV * cairo_antialias_to_sv (int val);
#define SvCairoAntialias(sv)		(cairo_antialias_from_sv (sv))
#define newSVCairoAntialias(val)	(cairo_antialias_to_sv (val))
int cairo_path_data_type_from_sv (SV * path_data_type);
SV * cairo_path_data_type_to_sv (int val);
#define SvCairoPathDataType(sv)		(cairo_path_data_type_from_sv (sv))
#define newSVCairoPathDataType(val)	(cairo_path_data_type_to_sv (val))
int cairo_format_from_sv (SV * format);
SV * cairo_format_to_sv (int val);
#define SvCairoFormat(sv)		(cairo_format_from_sv (sv))
#define newSVCairoFormat(val)	(cairo_format_to_sv (val))
int cairo_font_type_from_sv (SV * font_type);
SV * cairo_font_type_to_sv (int val);
#define SvCairoFontType(sv)		(cairo_font_type_from_sv (sv))
#define newSVCairoFontType(val)	(cairo_font_type_to_sv (val))
int cairo_hint_style_from_sv (SV * hint_style);
SV * cairo_hint_style_to_sv (int val);
#define SvCairoHintStyle(sv)		(cairo_hint_style_from_sv (sv))
#define newSVCairoHintStyle(val)	(cairo_hint_style_to_sv (val))
int cairo_pattern_type_from_sv (SV * pattern_type);
SV * cairo_pattern_type_to_sv (int val);
#define SvCairoPatternType(sv)		(cairo_pattern_type_from_sv (sv))
#define newSVCairoPatternType(val)	(cairo_pattern_type_to_sv (val))
int cairo_font_weight_from_sv (SV * font_weight);
SV * cairo_font_weight_to_sv (int val);
#define SvCairoFontWeight(sv)		(cairo_font_weight_from_sv (sv))
#define newSVCairoFontWeight(val)	(cairo_font_weight_to_sv (val))
int cairo_extend_from_sv (SV * extend);
SV * cairo_extend_to_sv (int val);
#define SvCairoExtend(sv)		(cairo_extend_from_sv (sv))
#define newSVCairoExtend(val)	(cairo_extend_to_sv (val))
int cairo_ps_level_from_sv (SV * ps_level);
SV * cairo_ps_level_to_sv (int val);
#define SvCairoPsLevel(sv)		(cairo_ps_level_from_sv (sv))
#define newSVCairoPsLevel(val)	(cairo_ps_level_to_sv (val))
int cairo_fill_rule_from_sv (SV * fill_rule);
SV * cairo_fill_rule_to_sv (int val);
#define SvCairoFillRule(sv)		(cairo_fill_rule_from_sv (sv))
#define newSVCairoFillRule(val)	(cairo_fill_rule_to_sv (val))
int cairo_font_slant_from_sv (SV * font_slant);
SV * cairo_font_slant_to_sv (int val);
#define SvCairoFontSlant(sv)		(cairo_font_slant_from_sv (sv))
#define newSVCairoFontSlant(val)	(cairo_font_slant_to_sv (val))
int cairo_hint_metrics_from_sv (SV * hint_metrics);
SV * cairo_hint_metrics_to_sv (int val);
#define SvCairoHintMetrics(sv)		(cairo_hint_metrics_from_sv (sv))
#define newSVCairoHintMetrics(val)	(cairo_hint_metrics_to_sv (val))
int cairo_status_from_sv (SV * status);
SV * cairo_status_to_sv (int val);
#define SvCairoStatus(sv)		(cairo_status_from_sv (sv))
#define newSVCairoStatus(val)	(cairo_status_to_sv (val))
int cairo_filter_from_sv (SV * filter);
SV * cairo_filter_to_sv (int val);
#define SvCairoFilter(sv)		(cairo_filter_from_sv (sv))
#define newSVCairoFilter(val)	(cairo_filter_to_sv (val))
int cairo_operator_from_sv (SV * operator);
SV * cairo_operator_to_sv (int val);
#define SvCairoOperator(sv)		(cairo_operator_from_sv (sv))
#define newSVCairoOperator(val)	(cairo_operator_to_sv (val))
int cairo_subpixel_order_from_sv (SV * subpixel_order);
SV * cairo_subpixel_order_to_sv (int val);
#define SvCairoSubpixelOrder(sv)		(cairo_subpixel_order_from_sv (sv))
#define newSVCairoSubpixelOrder(val)	(cairo_subpixel_order_to_sv (val))
int cairo_line_join_from_sv (SV * line_join);
SV * cairo_line_join_to_sv (int val);
#define SvCairoLineJoin(sv)		(cairo_line_join_from_sv (sv))
#define newSVCairoLineJoin(val)	(cairo_line_join_to_sv (val))
int cairo_surface_type_from_sv (SV * surface_type);
SV * cairo_surface_type_to_sv (int val);
#define SvCairoSurfaceType(sv)		(cairo_surface_type_from_sv (sv))
#define newSVCairoSurfaceType(val)	(cairo_surface_type_to_sv (val))
#ifdef CAIRO_HAS_SVG_SURFACE
int cairo_svg_version_from_sv (SV * svg_version);
SV * cairo_svg_version_to_sv (int val);
#define SvCairoSvgVersion(sv)		(cairo_svg_version_from_sv (sv))
#define newSVCairoSvgVersion(val)	(cairo_svg_version_to_sv (val))
#endif /* CAIRO_HAS_SVG_SURFACE */
