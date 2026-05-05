/**
 * Dummy data for development/testing only.
 * Covers all fields required by Zod validation (ordinaryLoanSchema).
 * Only loaded in dev mode — never imported in production paths.
 */

import type { Step1Data, Step2Data, Step3Data, Step4Data, Step5Data, Step6Data } from '@/types/form'

// ── Minimal programmatic signatures (~1KB each) ─────────────────────────────
const SIG1 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARgAAABLCAYAAACr45hhAAADbklEQVR4nO3d0VHjMBAGYGCuBYqgRCq4Eq8IisgND5mBjO04jlfalb7vDYYL2gT9Wimx7/VyubwARHgLeVQAAQNE0sEAYQQMEEbAAGEEDBBGwABhBAwQRsAAYQQMEEbAAGEEDBBGwABhBMwJ3j8+XZIOC17druG8YPn69/f1iYeD4ehgDtK1wH0C5kRCB34TMAcIEigQMCNM1NtzlxFqgtKHvJUPR3+O/ee4K9cEw3QwVniYR4ozmCqhs9a9LH1dpSYYJmBmm3Sz1QtpOphqK/5W93Lv+9lda8v+GlBPs0Peyoeje8Jl7ef3/ptelkIl83ipJcUZDH2sdSzf39fNUCZgKh+OPtq9VKhpr6rjZqKAOTJBR/jDzh4yS9u4pddHN0P5LVLWPf+RcKxg64xoK2hajY9xvGWZoNlX/CMy1rR3DLoZhulgZupeeobMo+8Y6WZIGzAzH47+lGVr9czb0boZhulgMoTM2d1LhppuPVqXboY0AVP5cLTy2Ft88E83Q9eAOWOCZlzxn9WrpohPFetmKLtFWtNiQkZ3L61DJvrxdTM0DZgzJ+go25PRrzHSzVC2g2m54rc6e2lRU48LGHUzhAbMiIejrfTYykT9ntE+BVx57EPdriEyYKJvf9AjHKNqynKriLWJmW3x6REgX8meg/QB02KCRk6cXt3X2TVlCZdM95uZoQP5SvA6r/kz+9ao+vizT6Tv5/R2bNevz3i+z6hb4CXuYFpO0MgVP8tW4sg4encJkeOsFiCtvX98XjLX91TAtJ6gZ0+kDAFzO45Hx1IlXCI7rcz1zu7pLVLvdrt6uJwtey3X8T3yOmaviYAOpucEPXtbkeEP+EhNGQ91H3HmWQw5pf6gXZRs4bLk3gpfPVy2PjfD5AHTe4LOcDHklhHqZQ5v1cJl7XfvnXRZxn+0pmqHusxtyi1SVcKFoQMm2+r/aBeTbfzP1pS1Bhi2g9n63wqrTMylkBnhUJf57A6YrBM001hambFmahqig7m3rcgajluqjBOeDpiKE3RUnn+mvB9MBkvnFNXD8XoxW/aL2mD4gPnmXRfIY4gzmD2s/tDecAEjSCCP4QJmidCBPoY7g7lyKAr9DRswQH9TbJGAPgQMEEbAAGEEDBBGwABhBAwQRsAAYQQMEEbAAGEEDBBGwABhBAzwEuU/ovmlNfMGUNgAAAAASUVORK5CYII='
const SIG2 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARgAAABLCAYAAACr45hhAAADuUlEQVR4nO3dwW7bMBCE4VjXPJ2fNE+Xs4McDAiCZVMSh5zd/b9LgbZwuJI4XNKue3s8Hl8AoLBIXhUACBgASnQwAGQIGAAyBAwAGQIGgAwBA0CGgAEgQ8AAkCFgAMgQMABkCBgAMgQMABkCBoAMAQNAhoABIEPAGLl/fz/WvwLR3fhGOw+vQuXn9/c2ZzRAgQ6GFR2IzbaDqbSiv9sSZa0ZNSyOk63SGcSnWitdi390rblYBUy1ydbapWWruzVcqtSd2eLctfxPtu2Ey/zQPWutuC3au6+Z73cF089gWlbxjOcx25paOpfoNe9pDZGs9We2OHYtLb9XcUJlXM1bO9e9vwtvi/tDtf7zT68R1ZEAzVT3pwWGkIlvce1asobM0W1Ptu7t6Ur3GvG+V7U4dy1nX9fV2bFmCNa1o4vMXshEvw4VyA959x6CK8ES8fCzx0F1xLp7X4eMB/6ZLRG7lgwreo9JEa3uHuHAlimWxfGsJVvI9Oo8Iq/UPZ8HQqZwwKi6lrM/e7beY4oUrE+KxYZzmWIBM6JrGfnazmOOFDLKZ4LPyxQJmJldi/NkG3ko61T306gFhy1T0oCZ0bVECRn1GNy7N4du1uE5qO7029QOweI6npFjcXzreua9UHwsAgM7GJeuxe3nvzNy5Z69as9+NjiXCRwwM89aokw2h45iVsjMDpdPP3d2+Fa0RO5a3EJm1gPseB8cxkXIBAmY7Y1y6lpaVJj4s7s3h87tFT4vE2SLFOnb1hy2JTPGMCtkHGqvei5zN69h+jfaZXjwnbaPo8fiVHvG8UZ/hyx1wIwIGccHtmKwZhv3/UBn4jb20gHT+4a4bg8qBmvUbuCeJExKBoxysrmGy+i6e752xS3lnqjXtFzAKCZbhEmmGGOEul1quhcLk9IB0ztk3LuXETVffb3s37S3J8s1a1E6YM7e7Cjh0nO8mcPl6LkMYdKuVMD0mGxRJ9qVuqPWPPvL2VEwYK5MtsgT7ezYI9esDJkK16CHkgFzNmSibY2ujr9quGzrr1RzbwTMyrsHKXq4HK2jergg+P9NPZvqHQJ3LQeWhAt6KRswV94dyLaSr+smXNBT6YBpCZksW6M1tkUYpXzAvPIMlUxbozPdW4YwxVxlD3m3WsIk44Rz+kd/yIcOpnFCVZpwlWqFFgHTMLEyT7jtNxVmrhXjETAgXCBDwGywogP9cMgLQIYOBoAMAQNAhoABIEPAAJAhYADIEDAAZAgYADIEDAAZAgaADAEDQIaAASBDwAD4UvkDii9kEjDDJmEAAAAASUVORK5CYII='
const SIG3 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARgAAABLCAYAAACr45hhAAAC8klEQVR4nO3dwW7aQBSGUciWp+uT9ulYU3WBFKFAbPBvz517ziZSpTb2jedjjKhzvt1uJ4CEr8i/CiAwQJIdDBAjMECMwAAxAgPECAwQIzBAjMAAMQIDxAgMECMwQIzAADECA8QIDBAjMECMwAAxAgPECAyny5/L7ftX2MrZM3l7+ykq17/X8zFHw2wEprHfdixCw6fcIjW15HbILROfsoNp5lk07rsVt0xsaYodjDcp183p1a3QT7dF//+e3QztdjBLFgzPZ/VqTmZL68AseUUVmuezWjobt0y0CszarXr3yGwRCLsZWgRmyYXuFff1vN4NrsgwbWDWXtwWQy60As40gXl1O/TbYukamT3Ou+tsmSgwW13EnV5x91z4IkPJwCQu3A6L4aiQdgo4xQOTDMHMkTl6kc88WyYIzNFb+8oLYZTzERmGC8wnb+Imvm+10IwSl9GPiYaBOXqRH/39Z17I1WdL4cCMdvGNvFArzK/6cW55vrOeW5nAjHrRjXpcVY+zcsBT/23lOsk5DxmYCgtj9GOsvFBHn+1SiUdWXIvNYKjAHPUm7mwLecRj6hKZLR4renkzTKPP5tDAVL2gRjv2GeJS7Xz2emG8fLAjGm1muwVmpMVZ/TwqLMaqsx394eeXSXY9mwZmtAtnCz6Cv99cR/iYwt7HMXt8NgnM0RfL7J80Tn2vbgGv+J5g9Wh+FJjZf2DfeQxCvdmOuOC6fU7n7cB0e6W98yCn/ea65eM93/332DkwXcOSnMGsb+buNYtOO+mpAyMu289CXNZfZ3YpkwVGWNbNxq8E+ZzfHtFsB/P4A7f1fD6bJTOyc1nGi1uzWyRheT6bn/78cV4WzHr3mbn26hniiXYzebUzERe6EZgD3z/wiszsvo4+gBktCYe40IEdTJg3c+nMDibsvlN5/Aod2MEAMXYwQIzAADECA8QIDBAjMECMwAAxAgPECAwQIzBAjMAAMQIDxAgMECMwQIzAADECA8QIDBAjMMAp5R/0P5P13Xh2SQAAAABJRU5ErkJggg=='
const SIG4 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARgAAABLCAYAAACr45hhAAADyElEQVR4nO3dDYoaQRDFcR1yhRzHQ+SkOUSOk0MYFrIgw3y1dnXXe/X/QQjsBqdLrWf1qJP78/m8AUCEJeRWAYCAARCJCQZAGAIGQBgCBkAYAgZAGAIGQBgCBkAYAgZAGAIGQBgCBkAYAgZAGAIGQJ2Aefz8xde7ARP3LJdrWAfLn7+/7/NWA8BmgmFqATylCJgthA6gb8kUJOttESEDaJseMGdcQ+a7Ltf6gOkBszW9VDi5uw4XQgauUk4wzlulvVqcatxCmNa0ZDz3svUzhwZ0qOEdTGx1pZxgqjSoY4i2TGyO9SJBwJxNL1d+p+bqBwmrNV21eqtZsobL3r9RfEIerXnrPlCs8WqoOtcL0S2ScshsrXVdj2PTHU1se/Wq14zJAdM6vVy9LeVwOfu5oiuPDVvEGiQmGMUGbAmXvd8rhOinoeo4vWFCwPSYXlQa8J1wabmtrN6tmy2TL5kJRi1k3g0Xp1f0T+tWrh0DA6bnuZez23e4ro3adrBn3U4BC8EJJnMD9mwEpUmt98XC2DL5WFSnl2wN2PO8S8sxZotaE1smD6GXzIzeGq2PEXmcljX0XMeI4Mq+tsz3AQy3SJle5aOf/FnPSYxserZMuhbl6SX6trM0mcKrdfQaOQGsyWKCyXI+ZmSQzpxiZm5LmWa0LMrTy8wGzHruZ/QxZ9TNCWAdFhPM6AbMNCGNXEuGcz9VtkwPkzq6v4s0Y3rZO37EGjK8ozFjDRnqbm3GLOtzX3+pCSZyq5SlySoEmuuW6fH/shSvf27Guk4ws6eXvbVEXR7CrcbZx+kh0+P0aAiPzPdpioDJFC4jvtHsVuPVY2SoO+OWgzApFjA9myNzk438FHGmumeGDGEyOGAyhkuvJlFosoiQyTq1ja6DMPmMfcB8EhJKTdYzCJXq7jnNECYJAyZ7uLzbMIpN1iNkFOu+4pN3axzqn+XHrYCvJ0jLE8ylyb7qiLg2i6LvOs6eBy71WkwwCtNL6yu8erh8sn6F8009fNfpWl8mdh+0O3K251YPF9d3ykZ9zQCJAkZtetlzNDKr1tV68tL906QQCxjlcLn6sXK1us7shYjD1Ia8Sm2RMl5bJcqV80uEC9IFjPL08upo7cp1vWq9nIFL3cij5ARzxK3Jqm4JIRgwLtPLuob139W2hK51Y77yE4x7uAASAeM2vVSz95jxWCJS+QmmkipbQoh9VYDpBUC6/zoWQG1skQCEIWAAhCFgAIQhYACEIWAAhCFgAIQhYACEIWAAhCFgAIQhYACEIWAAhCFgAIQhYADcovwDPRwtiEj6d3wAAAAASUVORK5CYII='
const SIG5 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARgAAABLCAYAAACr45hhAAADuklEQVR4nO3dQW6jQBCFYZstZ5pDzEnnEDmT1x55YSmyDDQNRb9X9X+bSIkcNxX6Ud3Gzv35fN4AIMIU8lsBgIABEIkOBkAYAgZAGAIGQBgCBkAYAgZAGAIGQBgCBkAYAgZAGAIGQBgCBkAYAgZAGALG0Pzn7/P3V0DVnY9r8PItVB4//+5jRgOso4MxstSx0MlAFQGTBCEDRQSMaYCwLIIDu4CpuMG5dKyfIVOpJvBgtclbcYOz5ZjpbqDKooN5TSCuzu2BSq2gQj5gtiZL5snU2pl8+37musDH5Na1vCZThb2HvcdEyEDR5Lyp2fIYR717TdVDhqW0HrlN3j2TK+Pm5hkb2WyG99UNiTuYtSXR0mMqLJV6Jkm1icUdzrom1yVRxpA5syPLVJc1Wxcllk2Fl0hHgmXr97hdxaOOIeMy8sjNh1mO38XkHi69j1FyZUBm6GRaX118f//zsRlq4GJIB8PVer0eZ4dLhg7vjGOhm0keMGd2La3PoT6RrhpvhpA56xjczhFnU6Zw2fO8Cq4cm/s9MmcG5OdyimWTcQczIlgcrlCjOgrHTiZyzI71cBIaMKO6lm/PrXTSjD6plWsz6vxxqYmbsIAZPYmUTxqFcSmMwaHDU6vLrXrAjOxaWsYy+oRROoGVxqL2d1OtTelNXqVwGfm8S9Q3VRXGpxAu356TjeCBHYxasChejVQmjvK4lMaidv6U7WDUw0X1fTkq9VF5+Vo1XLK8rD0PGu+hDkb5pFAaq8MVUGVT9crnzvb3nDdCZMQ4uwLG8aQYdWIQwjlqox7ILSwCxjVcRoSM4wTirQvj6zWbhcgpAeMeLFdPIsdweePNl/E1mxOFyOGAyRQuV01+1XX66PE7B++Vm6mPJDXp6mAyHHxkALiHS1QQZA+XvSHzSHjsh/ZgXoXLVJSr1s+uNYv6eIQjv8vJnGy+pPivAs4hkylczjqmjDWB2Yd+Z70hKcNEOnIjHuGC8gETtXmZIVyOhAzhgpfyAfNtAu3tYtxuG+/Bsgg9CJiDIVPpSt1So0r1wDYCZgXLgPaQWXoDIOFSGwFz4mSoOpn2/J8i1ELAdC6VMm/qbtk61kq1wDoCpiNkKmzqblkKEcIFvxEwjX7vNXz+rOqkeh/351fgjYBZ0DpZqk8qwgVryr9VYMvacqh6uABb6GA2ECJAPwKmE8EDbCNgGrCZCfRhDwZAGDoYAGEIGABhCBgAYQgYAGEIGABhCBgAYQgYAGEIGABhCBgAYQgYAGEIGABhCBgAtyj/ASxfSyz8jtV3AAAAAElFTkSuQmCC'
const SIG6 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARgAAABLCAYAAACr45hhAAADrElEQVR4nO3dQXKjMBCFYdvbOdMcwifNIXKmrD3lxVSlKAMC9KTX3f+3yWI8jtpID0kQfH+9XjcAUHhI3hUACBgASsxgAMgQMABkCBgAMgQMABkCBoAMAQNAhoABIEPAAJAhYADIEDAAZAgYADIEDAAZAgaADAEDoGbAPP/+ef3+CSCWu+sT7T6Fytf3z31OawCkmcFUnbEwY0M2lgFTMXiW4ZK5VtRhFzDLgbVcFmUceGs1ZawVtVgFTOuAqjTwKtWKfB4RNnUzb+7uzdg+vQaI4hHlilHGpdJaDZVD5l1nlVorsLhM3XIWP/NaZy2heiSAMuDWhHymz2CuBkbEs13rQFr7LCLWvIeN7pymBsyZgZLx7L1V0/vfsi+Z9gKXZVNc05ZIV6fDUZdKV9qdcQlxZqkYveZKpgRMr4ESreP1qDtLyBzdX8pSdzXDl0jKjuK8bOhVd4bl0pnN609LxWh1VzR9k/dKuEQ+g/WuO8pgWwva1s9j+Vr2Z7wNXSKpljTuS6VRdfd8bwVFe92PfXXDZjDKM6zz1Hlk3erf5xiGn46962dQ0ZCAmXGmdehkI+qOEDLqz4H9mcJLpJHh4jRdHh2qrsslh5OLw+dQ1fCAqdK5ZrTD7U8LZoeeS1+oTBowsw7w7I7l9vurtsGpHVXJ9mCc9gFGtsWh7pn7MmubrLMGNfszCWcwDh3MZYlSfR9I/TujzS6r6R4wToNsZGdyqntGu1zrX0PQJLlMPbOTzbw/xmVwjVguRQuXN+6fCRgwEc4KipBxr1sZMhHDJdP+zNO8vd2WSM4dTRkAznWr2xqpdpcTxVMQCM6feZeAidDRFJ0nQt2jHpVx9n0cuc8KSgVMpI7WM2Qi1a1+2NfR/x/B6L8hy+pSwETraD3b677vorqkHO2YX/WuN3N9oTZ53Q9ElcdDtDj6QHG3G+hGyV6fbcBEHWRXrxpEW59vaX2geIQb6JAoYKIPsrMhk/UMvhUyV59Ah9oOB0zWQXYmNDPUffRemUw1wyxgMnW4q0/zj1r3lr2aMtYM403e6B2udakUfUnY45hGP9YwD5isZ/C9kMk0a2v1v77lT0ASMJXO4C0bnLcCCBcMC5jloMo2yI58J4++NUDRO3mz39W4NVPLXDdgscmbfZBlrw8o99WxERA8wDkEzAJXUICg300NoBZmMABkCBgAMgQMABkCBoAMAQNAhoABIEPAAJAhYADIEDAAZAgYADIEDAAZAgaADAEDQIaAAXBT+Qd+cxawNhWNZQAAAABJRU5ErkJggg=='

// ── Helpers ──────────────────────────────────────────────────────────────────
function makeSig(base64: string) {
  return { signed: true, signed_at: new Date().toISOString(), signature_base64: base64 }
}

const addrChiangmai = {
  house_no: '123/4', moo: '5', road: 'ถนนห้วยแก้ว',
  tambon: 'ช้างเผือก', amphur: 'เมือง', province: 'เชียงใหม่'
}
const addrChiangmai2 = {
  house_no: '45/6', moo: '2', road: 'ถนนนิมมานเหมินท์',
  tambon: 'สุเทพ', amphur: 'เมือง', province: 'เชียงใหม่'
}
const addrLampang = {
  house_no: '78/9', moo: '3', road: '',
  tambon: 'พระบาท', amphur: 'เมือง', province: 'ลำปาง'
}
const addrNakhon = {
  house_no: '12/3', moo: '', road: 'ถนนสุขุมวิท',
  tambon: 'ในเมือง', amphur: 'เมือง', province: 'นครราชสีมา'
}

// ─────────────────────────────────────────────────────────────────────────────

export const dummyStep1: Step1Data = {
  title: 'ด.ต.',
  first_name: 'สมชาย',
  last_name: 'ใจดี',
  id_card: '3101234567891',
  position: 'ผู้บังคับหมู่',
  department: 'กก.สส.ภ.จว.เชียงใหม่',
  organization: 'สอ.ภ.6',
  phone: '081-234-5678',
  member_code: '12345',
  marital_status: 'married',
  spouse_name: 'นางสาวสมหญิง ใจดี',
  current_addr: addrChiangmai,
  register_addr: addrChiangmai2,
  salary: 25000,
  shares_amount: 150000,
  existing_debt: 50000,
}

export const dummyStep2: Step2Data = {
  loan_amount: 500000,
  loan_purpose: 'ซื้อที่ดินเพื่อปลูกบ้านพักอาศัยสำหรับครอบครัว',
  repayment_period: 60,
  payout_method: 'transfer',
  bank_name: 'ธนาคารไทยพาณิชย์',
  bank_account_no: '1234567890',
  bank_account_name: 'ด.ต.สมชาย ใจดี',
}

export const dummyStep3: Step3Data = {
  guarantors: [
    {
      name: 'ด.ต.วีระ สุขใจ',
      id_card: '3209876543219',
      position: 'ผู้บังคับหมู่',
      department: 'กก.1 บก.ปค.ภ.6',
      phone: '082-345-6789',
      member_code: '22222',
      current_addr: addrLampang,
      marital_status: 'single',
    },
    {
      name: 'ด.ต.มานะ ตั้งใจ',
      id_card: '3305551234567',
      position: 'สารวัตร',
      department: 'สภ.เมืองเชียงใหม่',
      phone: '083-456-7890',
      member_code: '33333',
      current_addr: addrNakhon,
      marital_status: 'married',
      spouse_name: 'นาง รัตนา ตั้งใจ',
    },
  ],
}

export const dummyStep4: Step4Data = {
  borrower_sig: makeSig(SIG1),
  spouse_sig: makeSig(SIG2),
  guarantor_sigs: [makeSig(SIG3), makeSig(SIG4)],
  guarantor_spouse_sigs: [{ signed: false }, makeSig(SIG5)],
  superior_sig: {
    ...makeSig(SIG6),
    signer_name: 'พ.ต.อ.สุรชัย ดีใจ',
    signer_position: 'ผกก.สส.ภ.จว.เชียงใหม่',
  },
  superior_opinion: 'true',
}

export const dummyStep5: Step5Data = {
  checklist_items: [
    true, true, true, true, true,
    true, true, true, true, true,
    true, true, true, true, true,
    false, false, false,
  ],
  limit_analysis: {
    total_income: 25000,
    total_deduction: 15000,
    net_income: 10000,
  },
}

export const dummyStep6: Step6Data = {
  contract_no: '001/2568',
  interest_rate: 5.75,
  effective_date: '2025-06-01',
  manager_sig: makeSig(SIG1),
  chairman_sig: makeSig(SIG2),
  witness_sig_1: makeSig(SIG3),
  witness_sig_2: makeSig(SIG4),
  manager_name: 'นางสาวสมฤดี บริหารดี',
  chairman_name: 'นายอุดม สหกรณ์ดี',
  witness_1_name: 'พ.ต.ต.วีระ สุขใจ',
  witness_2_name: 'ด.ต.มานะ ตั้งใจ',
}
