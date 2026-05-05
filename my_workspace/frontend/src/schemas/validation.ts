import { z } from 'zod';

/**
 * World-Class Validation Schema for MTCoopForm
 * Focuses on legal compliance and data integrity.
 */

const addressSchema = z.object({
  house_no: z.string().min(1, 'กรุณาระบุเลขที่บ้าน'),
  moo: z.string().optional(),
  road: z.string().optional(),
  tambon: z.string().min(1, 'กรุณาระบุแขวง/ตำบล'),
  amphur: z.string().min(1, 'กรุณาระบุเขต/อำเภอ'),
  province: z.string().min(1, 'กรุณาระบุจังหวัด'),
});

const signatureSchema = z.object({
  signed: z.boolean().refine(val => val === true, {
    message: 'กรุณาลงลายมือชื่อให้ครบถ้วน',
  }),
  signature_base64: z.string().optional(),
});

// Shared Steps
const step1Schema = z.object({
  title: z.string().min(1, 'กรุณาระบุคำนำหน้า'),
  first_name: z.string().min(1, 'กรุณาระบุชื่อ'),
  last_name: z.string().min(1, 'กรุณาระบุนามสกุล'),
  id_card: z.string().length(13, 'เลขบัตรประชาชนต้องมี 13 หลัก'),
  member_code: z.string().min(1, 'กรุณาระบุเลขทะเบียนสมาชิก'),
  position: z.string().min(1, 'กรุณาระบุตำแหน่ง'),
  department: z.string().min(1, 'กรุณาระบุสังกัด'),
  salary: z.coerce.number().min(1, 'กรุณาระบุเงินเดือน'),
  marital_status: z.enum(['single', 'married']),
  current_addr: addressSchema,
  register_addr: addressSchema,
});

const step4Schema = z.object({
  borrower_sig: signatureSchema,
  superior_sig: signatureSchema,
});

// Ordinary Loan
export const ordinaryLoanSchema = z.object({
  step1: step1Schema,
  step2: z.object({
    loan_amount: z.coerce.number().min(1000, 'ยอดเงินกู้ขั้นต่ำคือ 1,000 บาท'),
    repayment_period: z.coerce.number().min(1, 'กรุณาระบุจำนวนงวด'),
    loan_purpose: z.string().min(5, 'กรุณาระบุวัตถุประสงค์การขอกู้'),
    payout_method: z.enum(['transfer', 'cash', 'cheque']),
    bank_name: z.string().optional(),
    bank_account_no: z.string().optional(),
    bank_account_name: z.string().optional(),
  }).refine(
    (s) => s.payout_method !== 'transfer' || (!!s.bank_name && !!s.bank_account_no),
    { message: 'กรุณาระบุข้อมูลบัญชีธนาคาร', path: ['bank_account_no'] }
  ),
  step3: z.object({
    guarantors: z.array(z.object({
      name: z.string().min(1, 'กรุณาระบุชื่อผู้ค้ำประกัน'),
      member_code: z.string().min(1, 'กรุณาระบุเลขทะเบียนสมาชิก'),
      id_card: z.string().length(13, 'เลขบัตรประชาชนต้องมี 13 หลัก'),
      marital_status: z.enum(['single', 'married']),
      current_addr: addressSchema,
    })).min(1, 'ต้องมีผู้ค้ำประกันอย่างน้อย 1 ท่าน'),
  }),
  step4: step4Schema,
}).refine((data) => {
  if (data.step1.marital_status === 'married') {
    return data.step4.borrower_sig.signed === true; 
  }
  return true;
}, {
  message: 'คู่สมรสต้องลงนามยินยอม',
  path: ['step4', 'spouse_sig'],
});

// Emergency Loan
export const emergencyLoanSchema = z.object({
  step1: step1Schema,
  step2: z.object({
    loan_amount: z.coerce.number().min(1000, 'ยอดเงินกู้ขั้นต่ำคือ 1,000 บาท').max(50000, 'ยอดเงินกู้สูงสุดไม่เกิน 50,000 บาท'),
    repayment_period: z.coerce.number().min(1, 'กรุณาระบุจำนวนงวด').max(12, 'สูงสุดไม่เกิน 12 งวด'),
    loan_purpose: z.string().min(5, 'กรุณาระบุวัตถุประสงค์การขอกู้'),
    payout_method: z.enum(['transfer', 'cash']),
  }),
  step4: step4Schema,
}).refine((data) => {
  if (data.step1.marital_status === 'married') {
    return data.step4.borrower_sig.signed === true;
  }
  return true;
}, {
  message: 'คู่สมรสต้องลงนามยินยอม',
  path: ['step4', 'spouse_sig'],
});

export type OrdinaryLoanFormData = z.infer<typeof ordinaryLoanSchema>;
export type EmergencyLoanFormData = z.infer<typeof emergencyLoanSchema>;
