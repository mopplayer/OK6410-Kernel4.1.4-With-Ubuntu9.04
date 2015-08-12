/*
 * Copyright (c) 2004-2005 by the cairo perl team (see the file README)
 *
 * Licensed under the LGPL, see LICENSE file for more information.
 *
 * $Header: /cvs/cairo/cairo-perl/cairo-perl.h,v 1.13 2007-10-24 16:32:05 tsch Exp $
 *
 */

#ifndef _CAIRO_PERL_H_
#define _CAIRO_PERL_H_

#include "EXTERN.h"
#include "perl.h"
#include "XSUB.h"

#include <cairo.h>

#ifdef CAIRO_HAS_PNG_SURFACE
# include <cairo-png.h>
#endif

#ifdef CAIRO_HAS_PS_SURFACE
# include <cairo-ps.h>
#endif

#ifdef CAIRO_HAS_PDF_SURFACE
# include <cairo-pdf.h>
#endif

#ifdef CAIRO_HAS_SVG_SURFACE
# include <cairo-svg.h>
#endif

#if CAIRO_HAS_FT_FONT
# include <cairo-ft.h>
#endif

#include <cairo-perl-auto.h>

/*
 * standard object and struct handling
 */
void *cairo_object_from_sv (SV *sv, const char *package);
SV *cairo_object_to_sv (void *object, const char *package);

void *cairo_struct_from_sv (SV *sv, const char *package);
SV *cairo_struct_to_sv (void *object, const char *package);

/*
 * custom struct handling
 */
SV * newSVCairoFontExtents (cairo_font_extents_t *extents);

SV * newSVCairoTextExtents (cairo_text_extents_t *extents);

SV * newSVCairoGlyph (cairo_glyph_t *glyph);
cairo_glyph_t * SvCairoGlyph (SV *sv);

SV * newSVCairoPath (cairo_path_t *path);
cairo_path_t * SvCairoPath (SV *sv);

#if CAIRO_VERSION >= CAIRO_VERSION_ENCODE(1, 4, 0)

SV * newSVCairoRectangle (cairo_rectangle_t *rectangle);

#endif

/*
 * special treatment for surfaces
 */
SV * cairo_surface_to_sv (cairo_surface_t *surface);
#undef newSVCairoSurface
#undef newSVCairoSurface_noinc
#define newSVCairoSurface(object)	(cairo_surface_to_sv (cairo_surface_reference (object)))
#define newSVCairoSurface_noinc(object)	(cairo_surface_to_sv (object))

/*
 * special treatment for patterns
 */
SV * cairo_pattern_to_sv (cairo_pattern_t *surface);
#undef newSVCairoPattern
#undef newSVCairoPattern_noinc
#define newSVCairoPattern(object)	(cairo_pattern_to_sv (cairo_pattern_reference (object)))
#define newSVCairoPattern_noinc(object)	(cairo_pattern_to_sv (object))

#endif /* _CAIRO_PERL_H_ */
