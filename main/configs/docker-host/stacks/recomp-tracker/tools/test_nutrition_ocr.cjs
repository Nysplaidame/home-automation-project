const { test } = require('node:test');
const assert = require('node:assert/strict');
const { parseLabel } = require('../static/nutrition-ocr.js');

test('UK single column: kcal, decimal commas, zero; ignore sugar and saturates', () => {
  const result = parseLabel('Per 100g\nEnergy 840kJ / 200kcal\nFat 4,5g\nof which saturates 2g\nCarbohydrate 20g\nof which sugars 8g\nProtein 0g');
  assert.deepEqual(result.values, { calories: 200, protein: 0, carbs: 20, fat: 4.5 });
  assert.equal(result.basis, '100g'); assert.deepEqual(result.warnings, []);
});
test('multiple columns require explicit selection, without mixing single-value rows', () => {
  const label = 'Per 100ml Per 30ml\nEnergy 200kcal 60kcal\nFat 10g 3g\nCarbohydrate 20g 6g\nProtein 5g 1.5g';
  assert.deepEqual(parseLabel(label).values, {});
  assert.deepEqual(parseLabel(label, 1).values, { calories: 60, protein: 1.5, carbs: 6, fat: 3 });
  assert.equal(parseLabel(label).basis, '100ml');
  assert.equal(parseLabel(label + '\nProtein 3g', 0).values.protein, undefined);
});
test('US values exclude percentage daily values; serving basis stays unconfirmed', () => {
  const result = parseLabel('Serving size 30g\nCalories 150\nTotal Fat 6g 8%\nTotal Carbohydrate 18g 7%\nProtein 3g');
  assert.deepEqual(result.values, { calories: 150, protein: 3, carbs: 18, fat: 6 });
  assert.equal(result.basis, null);
});
test('uncertain macros stay absent; labelled kJ converts with a review warning', () => {
  const result = parseLabel('Energy 850kJ\nFat <0.5g\nProtein 4g\nProtein 8g\nSugars 9g\nSaturates 2g');
  assert.deepEqual(result.values, { calories: 203.15 }); assert.match(result.warnings.join(' '), /converted from kJ/);
  assert.deepEqual(parseLabel('').values, {});
});
test('standalone kcal, split energy rows, split unit and OCR unit spelling fill calories', () => {
  for (const label of ['200kcal', 'Energy\n840kJ\n200kcal', 'Energy 840kJ\n(200 kcal)', 'Calories\n200', 'Energy 840kJ / 200kcaI', '200\nkcal', 'Energy\n840\nkJ\n200\nkcal', 'kcal: 200']) {
    assert.equal(parseLabel(label).values.calories, 200, label);
  }
});
test('explicit kJ/kcal header pairs preserve nutrition column alignment', () => {
  assert.equal(parseLabel('Energy (kJ/kcal) 840/200').values.calories, 200);
  assert.equal(parseLabel('Energy (kJ/kcal)\n840/200 420/100', 1).values.calories, 100);
  assert.equal(parseLabel('Energy (kcal/kJ) 200/840').values.calories, 200);
  assert.deepEqual(parseLabel('Energy 840kJ 200kcal 420kJ 100kcal').values, {});
});
test('malformed OCR digits are not silently truncated to zero', () => {
  assert.deepEqual(parseLabel('2O0kcal\nFat 4O0g').values, {});
  assert.equal(parseLabel('Fat .5g').values.fat, .5);
});
test('conflicting basis and absent selected column are not guessed', () => {
  const result = parseLabel('per 100g per 100ml\nFat 5g\nProtein 3g 1g', 1);
  assert.equal(result.basis, null); assert.equal(result.values.fat, undefined);
});
test('negative values and unsupported macro units cannot become grams', () => {
  assert.deepEqual(parseLabel('Fat -5g\nProtein 0.5mg\nCarbohydrate less than 1g').values, {});
});
