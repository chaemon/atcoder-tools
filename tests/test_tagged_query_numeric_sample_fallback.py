from atcodertools.fmtprediction.tagged_query import NoTaggedQueryPredictionError, _extract_variant_definitions_with_numeric_sample_fallback

def _extract_variant_definition_candidates_with_sample_fallback(blocks, samples):
    return (_extract_variant_definitions_with_numeric_sample_fallback(blocks, samples),)

class _Sample:

    def __init__(self, text):
        self._text = text

    def get_input(self):
        return self._text

def _single_candidate(blocks, sample):
    candidates = _extract_variant_definition_candidates_with_sample_fallback(blocks, [_Sample(sample)])
    assert len(candidates) == 1
    return candidates[0]

def test_incompatible_symbolic_candidate_uses_numeric_sample_tags():
    definitions = _single_candidate(['A_1 B_1 C_1\nA_M B_M C_M\nD_1 dots D_K\n'], '3\n1 10\n2 20 30\n3 40\n')
    assert [definition.tag for definition in definitions] == [1, 2, 3]
    assert [definition.argument_names for definition in definitions] == [('arg1',), ('arg1', 'arg2'), ('arg1',)]

def test_compatible_structural_numeric_candidate_is_preserved():
    definitions = _single_candidate(['1 X\n2 Y Z\n3 W\n'], '3\n1 10\n2 20 30\n3 40\n')
    assert [definition.argument_names for definition in definitions] == [('X',), ('Y', 'Z'), ('W',)]

def test_unknown_multiline_window_keeps_existing_candidate():
    definitions = _single_candidate(['1 X\n2 Y Z\n'], '2\n1\n10\n2\n20 30\n')
    assert [definition.tag for definition in definitions] == [1, 2]
    assert [definition.argument_names for definition in definitions] == [('X',), ('Y', 'Z')]

def test_equal_width_numeric_rows_do_not_steal_homogeneous_lane():
    try:
        _single_candidate(['A_1 X\nA_2 Y\nA_3 Z\n'], '3\n1 10\n2 20\n3 30\n')
    except NoTaggedQueryPredictionError:
        pass
    else:
        raise AssertionError('equal-width numeric rows must not invent tagged variants')
