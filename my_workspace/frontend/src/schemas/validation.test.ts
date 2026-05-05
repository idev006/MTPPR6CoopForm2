/**
 * validation.test.ts — Regression tests for Sprint 12 H-03, H-04
 * Covers: id_card length, loan_amount min, guarantor min, bank required on transfer,
 *         address fields required, emergency loan max constraints
 */
import { describe, it, expect } from 'vitest'
import { ordinaryLoanSchema, emergencyLoanSchema } from './validation'

const validAddress = {
  house_no: '1',
  tambon: 'ลาดพร้าว',
  amphur: 'ลาดพร้าว',
  province: 'กรุงเทพมหานคร',
}

const validStep1 = {
  title: 'ด.ต.',
  first_name: 'สมชาย',
  last_name: 'ใจดี',
  id_card: '3101234567891',
  member_code: 'T001',
  position: 'ผู้บังคับหมู่',
  department: 'กก.สส.',
  salary: 25000,
  marital_status: 'single' as const,
  current_addr: validAddress,
  register_addr: validAddress,
}

const validGuarantor = {
  name: 'ด.ต.วีระ สุขใจ',
  member_code: 'T002',
  id_card: '3109876543210',
  marital_status: 'single' as const,
  current_addr: validAddress,
}

describe('ordinaryLoanSchema', () => {
  it('passes with valid full data', () => {
    const result = ordinaryLoanSchema.safeParse({
      step1: validStep1,
      step2: {
        loan_amount: 100000,
        repayment_period: 24,
        loan_purpose: 'ซื้อที่ดินเพื่อปลูกบ้าน',
        payout_method: 'cash',
      },
      step3: { guarantors: [validGuarantor] },
      step4: {
        borrower_sig: { signed: true },
        superior_sig: { signed: true },
      },
    })
    expect(result.success).toBe(true)
  })

  it('rejects id_card shorter than 13 digits', () => {
    const result = ordinaryLoanSchema.safeParse({
      step1: { ...validStep1, id_card: '123456789' },
      step2: { loan_amount: 1000, repayment_period: 1, loan_purpose: 'xxxxx', payout_method: 'cash' },
      step3: { guarantors: [validGuarantor] },
      step4: { borrower_sig: { signed: true }, superior_sig: { signed: true } },
    })
    expect(result.success).toBe(false)
  })

  it('rejects loan_amount below 1000', () => {
    const result = ordinaryLoanSchema.safeParse({
      step1: validStep1,
      step2: { loan_amount: 500, repayment_period: 1, loan_purpose: 'xxxxx', payout_method: 'cash' },
      step3: { guarantors: [validGuarantor] },
      step4: { borrower_sig: { signed: true }, superior_sig: { signed: true } },
    })
    expect(result.success).toBe(false)
  })

  it('rejects empty guarantors array', () => {
    const result = ordinaryLoanSchema.safeParse({
      step1: validStep1,
      step2: { loan_amount: 10000, repayment_period: 12, loan_purpose: 'xxxxx', payout_method: 'cash' },
      step3: { guarantors: [] },
      step4: { borrower_sig: { signed: true }, superior_sig: { signed: true } },
    })
    expect(result.success).toBe(false)
  })

  it('rejects transfer payout without bank_account_no', () => {
    const result = ordinaryLoanSchema.safeParse({
      step1: validStep1,
      step2: {
        loan_amount: 10000,
        repayment_period: 12,
        loan_purpose: 'xxxxx',
        payout_method: 'transfer',
        // bank_name and bank_account_no missing
      },
      step3: { guarantors: [validGuarantor] },
      step4: { borrower_sig: { signed: true }, superior_sig: { signed: true } },
    })
    expect(result.success).toBe(false)
  })

  it('passes transfer payout with bank info provided', () => {
    const result = ordinaryLoanSchema.safeParse({
      step1: validStep1,
      step2: {
        loan_amount: 10000,
        repayment_period: 12,
        loan_purpose: 'ซื้อที่ดินเพื่อปลูกบ้าน',
        payout_method: 'transfer',
        bank_name: 'SCB',
        bank_account_no: '1234567890',
        bank_account_name: 'สมชาย ใจดี',
      },
      step3: { guarantors: [validGuarantor] },
      step4: { borrower_sig: { signed: true }, superior_sig: { signed: true } },
    })
    expect(result.success).toBe(true)
  })
})

describe('emergencyLoanSchema', () => {
  it('rejects loan_amount above 50000', () => {
    const result = emergencyLoanSchema.safeParse({
      step1: validStep1,
      step2: {
        loan_amount: 60000,
        repayment_period: 6,
        loan_purpose: 'ค่ารักษาพยาบาล',
        payout_method: 'cash',
      },
      step4: { borrower_sig: { signed: true }, superior_sig: { signed: true } },
    })
    expect(result.success).toBe(false)
  })

  it('rejects repayment_period above 12 months', () => {
    const result = emergencyLoanSchema.safeParse({
      step1: validStep1,
      step2: {
        loan_amount: 10000,
        repayment_period: 24,
        loan_purpose: 'ค่ารักษาพยาบาล',
        payout_method: 'cash',
      },
      step4: { borrower_sig: { signed: true }, superior_sig: { signed: true } },
    })
    expect(result.success).toBe(false)
  })
})
