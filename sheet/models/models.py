from odoo import models, fields, api, _
from datetime import datetime


class Enquiry(models.Model):
    _name = 'enquiry'
    _description = 'Enquiry'


    name = fields.Char(string='Student Name')
    enquiry_id = fields.Char(string='Enquiry ID', readonly = True)
    class_name = fields.Char(string="Class Name")
    age = fields.Integer(string='Age')
    address = fields.Char(string="Address")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    dob = fields.Date(string="Date of Birth")
    parent_name = fields.Char(string='Parent Name')
    phone_number = fields.Char(string='Phone Number')
    parent_occupation = fields.Char(string='Parent Occupation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ], default='draft', string='State')
    create_uid = fields.Many2one('res.users', 'Creator', readonly=True, default=lambda self: self.env.user)
    
    def action_confirm(self):
        self.state = 'confirmed'

        
        student = self.env['student.profile'].search([('name', '=', self.name), ('phone_number', '=', self.phone_number)])
        if not student:
            
            student_vals = {
                'name': self.name,
                'class_name': self.class_name,
                'address': self.address,
                'gender': self.gender,
                'dob': self.dob,
                'age': self.age,
                'parent_name': self.parent_name,
                'phone_number': self.phone_number,
                'parent_occupation': self.parent_occupation,
            }
            student = self.env['student.profile'].create(student_vals)
        
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Enquiry',
            'view_mode': 'tree',
            'res_model': 'enquiry',
            'target': 'current',
        }
        


    def action_reject(self):
        self.state = 'rejected'


    @api.onchange('dob')
    def _onchange_dob(self):
        if self.dob:
            today = datetime.today().date()
            dob = fields.Date.from_string(self.dob)
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            self.age = age

    @api.model
    def _generate_enquiry_id(self):
       
        last_enquiry = self.search([], order='id desc', limit=1)
        if last_enquiry and last_enquiry.enquiry_id.startswith('ENQ'):
            try:
                
                last_id = last_enquiry.enquiry_id.strip().upper().replace(' ', '')
                number = int(last_id.split('ENQ')[-1]) + 1
                
                return f'ENQ{str(number).zfill(4)}'
            except ValueError:
                
                return 'ENQ0001'
        else:
            return 'ENQ0001'

    @api.model
    def create(self, vals):
        
        if 'enquiry_id' not in vals or not vals['enquiry_id']:
            vals['enquiry_id'] = self._generate_enquiry_id()
        return super(Enquiry, self).create(vals)          
    

    @api.model
    def _generate_enqu_id(self):
        sequence_obj = self.env['ir.sequence']
        sequence = sequence_obj.next_by_code('your.enquiry.sequence')
        return sequence





class StudentProfile(models.Model):
    _name = 'student.profile'
    _description = 'Student Profile'

    name = fields.Char(string='Student Name', required=False)
    address = fields.Char(string="Address")
    class_name = fields.Char(string="Class Name")

    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', required=False)
    student_id = fields.Char(string='Student ID', required=False, unique=True, copy=False, readonly=True, default=lambda self: self._generate_student_id())
    dob = fields.Date(string='Date of Birth', required=False)
    parent_name = fields.Char(string='Parent Name')  
    phone_number = fields.Char(string='Phone Number') 
    parent_occupation = fields.Char(string='Parent Occupation')  
    exam_count = fields.Integer(string="Exam Count", compute='_compute_exam_count')
    event_count = fields.Integer(string="Event Count", compute='_compute_event_count')
    assignment_count = fields.Integer(string="Assignment Count", compute='_compute_assignment_count')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string="Status", default='draft', tracking=True)  
    

    def action_confirm(self):
        self.state = 'confirmed'

       
        student_record = self.env['student'].search([('student_name', '=', self.name), ('stu_contact', '=', self.phone_number)])
        if not student_record:
            
            student_vals = {
                'student_name': self.name,
                'stu_id': self.student_id,
                'stu_address': self.address,
                'stu_contact': self.phone_number,
                'stu_location': self.address,  
            }
            self.env['student'].create(student_vals)
        
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Profile',
            'view_mode': 'form',
            'res_model': 'student.profile',
            'res_id': self.id, 
            'target': 'current',
        }
 

    @api.depends('name')
    def _compute_exam_count(self):
        for student in self:
            student.exam_count = self.env['exam'].search_count([('student_ids', 'in', student.id)])

    def action_view_exams(self):
        self.ensure_one()
        exams = self.env['exam'].search([('student_ids', 'in', self.id)])
        action = self.env.ref('teacher.exam_action').read()[0]  # Replace with your actual action ID
        action['domain'] = [('id', 'in', exams.ids)]
        return action

    @api.depends('name')
    def _compute_event_count(self):
        for student in self:
            student.event_count = self.env['event'].search_count([('student_name', 'in', student.id)])

    def action_view_events(self):
        self.ensure_one()
        event = self.env['event'].search([('student_name', 'in', self.id)])
        action = self.env.ref('teacher.event_action').read()[0]  # Replace with your actual action ID
        action['domain'] = [('id', 'in', event.ids)]
        return action

    @api.depends('name')
    def _compute_assignment_count(self):
        for student in self:
            student.assignment_count = self.env['assignment'].search_count([('student_ids', 'in', student.id)])

    def action_view_assignment(self):
        self.ensure_one()
        assignments = self.env['assignment'].search([('student_ids', 'in', self.id)])
        action = self.env.ref('teacher.assignment_action').read()[0]  # Replace with your actual action ID
        action['domain'] = [('id', 'in', assignments.ids)]
        return action


    @api.onchange('dob')
    def _onchange_dob(self):
        if self.dob:
            today = datetime.today().date()
            dob = fields.Date.from_string(self.dob)
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            self.age = age





    

    @api.model
    def _generate_student_id(self):
        last_student = self.search([], order='id desc', limit=1)
        if last_student and last_student.student_id.startswith('STU'):
            try:
                
                last_id = last_student.student_id.strip().upper().replace(' ', '')
                number = int(last_id.split('STU')[-1]) + 1
                return f'STU{str(number).zfill(4)}'
            except ValueError:
                
                return 'STU0001'
        else:
            return 'STU0001'

    @api.model
    def create(self, vals):
        if 'student_id' not in vals or not vals['student_id']:
            vals['student_id'] = self._generate_student_id()
        return super(StudentProfile, self).create(vals)

    
   

class Exam(models.Model):
    _name = 'exam'
    _description = 'Exam Details'

    name = fields.Char(string='Exam Name', required=True)
    exam_date = fields.Date(string='Exam Date', required=True)
    total_marks = fields.Integer(string='Total Marks', compute='_compute_total_marks', store=True)
    passing_marks = fields.Integer(string='Passing Marks', required=True)
    student_ids = fields.Many2many('student.profile', string='Students')
    marks = fields.Integer(string='Marks')
    pass_fail = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string='Pass/Fail', compute='_compute_exam_pass_fail', store=True)
    grade = fields.Char(string='Grade')
    exam_details_ids = fields.One2many('exam.details', 'exam_id', string="Exam Details")
    subtotal = fields.Integer(string='Subtotal', compute='_compute_subtotal', store=True)
    student_id = fields.Many2one('student.profile', string='Student', required=True) 
    
    
    @api.depends('exam_details_ids.marks')
    def _compute_total_marks(self):
        for record in self:
            total = sum(detail.marks for detail in record.exam_details_ids)
            record.total_marks = total

    @api.depends('exam_details_ids.marks')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = sum(detail.marks for detail in record.exam_details_ids)

    @api.depends('exam_details_ids.pass_fail')
    def _compute_exam_pass_fail(self):
        for record in self:
            if any(detail.pass_fail == 'fail' for detail in record.exam_details_ids):
                record.pass_fail = 'fail'
            else:
                record.pass_fail = 'pass'

    

class ExamDetails(models.Model):
    _name = 'exam.details'

    exam_id = fields.Many2one('exam', string="Exam", ondelete='cascade')
    subject_name_id = fields.Many2one('subject.name', string='Subject Name', required=False)
    # subject = fields.Char(string="Subject", required=True)
    marks = fields.Integer(string="Marks")
    pass_fail = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string="Pass/Fail", compute='_compute_pass_fail', store=True)
    grade = fields.Char(string="Grade")

    @api.depends('marks', 'exam_id.passing_marks')
    def _compute_pass_fail(self):
        for record in self:
            if record.marks >= record.exam_id.passing_marks:
                record.pass_fail = 'pass'
            else:
                record.pass_fail = 'fail'


class SchoolClass(models.Model):
    _name = 'school.class'
    _description = 'Class Details'

    subject_name_id = fields.Many2one('subject.name', string='Subject Name', ondelete='cascade')
    name = fields.Char(string='Class Name', required=True)
    section = fields.Char(string='Class Section', required=True)
    teacher_name = fields.Char(string='Teacher Name', required=True)
    subject = fields.Many2many('subject.name', string='Subject')
    student_ids = fields.Many2many('student.profile', string='Students')

class SubjectName(models.Model):
    _name = 'subject.name'
    _rec_name = 'subject_name'

    subject_name = fields.Char(string="Subject Name")



class Event(models.Model):
    _name = 'event'
    _description = 'School Event'

    event_name_id = fields.Many2one('event.name', string='Event Name', required=True, ondelete='cascade')
    student_name = fields.Many2many('student.profile', string='Student Name')
    event_date = fields.Date(string='Event Date', required=True)
    location = fields.Char(string='Location', required=True)
    description = fields.Text(string='Description')
   
    student_id = fields.Many2one('student.profile', string='Student', required=True)
    

    
    
    @api.depends('student_name')
    def _compute_participant_count(self):
        for event in self:
            event.participant_count = len(event.student_name)

    @api.constrains('student_name')
    def _check_participant_limit(self):
        for event in self:
            if len(event.student_name) > 20:
                raise ValidationError('The maximum limit of 20 participants has been reached for this event.')



class EventName(models.Model):
    _name = 'event.name'
    _rec_name = 'event_name'

    event_name = fields.Char(string="Event Name")


class Assignment(models.Model):
    _name = 'assignment'
    _description = 'Assignment Details'

    name = fields.Char(string='Assignment Name', required=False)
    due_date = fields.Date(string='Due Date', required=False)
    subject = fields.Many2many('subject.name', string='Subject')
    description = fields.Text(string='Description')
    student_ids = fields.Many2many('student.profile', string='Students')
    class_id = fields.Many2one('school.class', string='Class', required=False) 
    student_id = fields.Many2one('student.profile', string='Student', required=False) 
    
    
   



class Sports(models.Model):
    _name = 'sports'
    _description = 'Sport Activity'

    name = fields.Char(string='Sports Name', required=True)
    sport_date = fields.Date(string='Sports Date', required=True)
    location = fields.Char(string='Location', required=True)
    description = fields.Text(string='Description')
    student_ids = fields.Many2many('student.profile', string='Participants')




 
class TeacherProfile(models.Model):
    _name = 'teacher.profile'
    _description = 'Teacher Profile'

    name = fields.Char(string='Teacher Name', required=True)
    age = fields.Integer(string='Age', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', required=True)
    teacher_id = fields.Char(string='Teacher ID', required=True, unique=True, readonly=True, default=lambda self: _('New'))
    # student_id = fields.Many2one('student.profile', string='Associated Student')
    teacher_class = fields.Many2many('student.profile', string='Class')
    teacher_ph_no = fields.Char(string='Phone Number', required=True)  
    teacher_email = fields.Char(string='Email ID', required=True)


class BusManagement(models.Model):
    _name = 'bus.management'
    _description = 'Bus Management'

    student_id = fields.Many2one('student', string='Student')
    bus_id = fields.Many2one('bus', string='Bus')
    bus_location = fields.Char(string="Bus Location")
    stu_location = fields.Char(string="Student Location")



    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed')],
        string='State',
        default='draft'
    )

    @api.onchange('student_id')
    def _onchange_student_id(self):
        if self.student_id:
            
            self.stu_location = self.student_id.stu_location or ''

    def action_confirm(self):
       
        self.state = 'confirm'
        
        
        if self.student_id and self.bus_id:
            
            bus = self.bus_id
            
            bus_location = bus.bus_location or ''
            bus_name = bus.bus_name or ''
            
           
            self.student_id.write({
                'bus_id': bus.id,
                'bus_location': bus_location,
                'bus_name': bus_name,
            })

    def action_draft(self):
        self.state = 'draft'

class Student(models.Model):
    _name = 'student'
    _description = 'Student'
    _rec_name = 'student_name'

    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed')],
        string='State',
        default='draft'
    )
    student_name = fields.Char(string='Student Name')
    stu_id = fields.Char(string='Student ID')
    stu_fee = fields.Float(string='Fee')
    stu_contact = fields.Char(string='Contact')
    stu_address = fields.Char(string='Address')
    stu_location = fields.Char(string='Student Location')
    bus_location = fields.Char(string='Bus Location')
    bus_id = fields.Many2one('bus', string='Bus')
    bus_name = fields.Char(string='Bus Name')

class Bus(models.Model):
    _name = 'bus'
    _description = 'Bus'
    _rec_name = 'bus_name'

    bus_code = fields.Integer(string="Bus Code")
    bus_name = fields.Char(string="Bus Name")
    bus_driver = fields.Char(string="Bus Driver")
    bus_location = fields.Char(string="Bus Location")
    phone_no = fields.Char(string="Phone Number")
    travel = fields.Char(string="Travelling")    